import spacy
from spacy.util import minibatch, compounding
import random
from spacy.training.example import Example
from pathlib import Path
from spacy.training.iob_utils import offsets_to_biluo_tags

nlp = spacy.load("fr_core_news_sm")

ner = nlp.get_pipe("ner")
LABEL_MARCHE = "NUM_MARCHE"
LABEL_VERSION = "VERSION_DOCUMENT"
LABEL_ORG = "ORG"
LABEL_LOC = "LOC"

for label in [LABEL_MARCHE, LABEL_VERSION, LABEL_ORG, LABEL_LOC]:
    ner.add_label(label)

TRAIN_DATA = [ ] # Labeled Training Data (Confidential)

random.shuffle(TRAIN_DATA)
split = int(len(TRAIN_DATA) * 0.8)
train_data = TRAIN_DATA[:split]
valid_data = TRAIN_DATA[split:]

pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

def evaluate_loss(nlp, data):
    losses = {}
    for text, annotation in data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotation)
        nlp.update([example], losses=losses, drop=0.0, sgd=None)  
    return losses.get("ner", 0.0)

optimizer = nlp.resume_training()
best_loss = float('inf')
patience = 5
no_improve = 0
output_dir = Path("./modele_ner_doc")
output_dir.mkdir(exist_ok=True)

with nlp.disable_pipes(*other_pipes):
    sizes = compounding(1.0, 4.0, 1.001)
    for iteration in range(30):
        random.shuffle(train_data)
        batches = minibatch(train_data, size=sizes)
        losses = {}
        for batch in batches:
            for text, annotation in batch:
                try:
                    doc_tmp = nlp.make_doc(text)
                    biluo = offsets_to_biluo_tags(doc_tmp, annotation["entities"])
                    if any(t == "-" for t in biluo):
                        continue
                except Exception:
                    continue
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotation)
                nlp.update([example], sgd=optimizer, drop=0.35, losses=losses)
        print(f"Iteration {iteration+1}, train losses: {losses}")

        val_loss = evaluate_loss(nlp, valid_data)
        print(f"  Validation loss: {val_loss:.3f}")

        if val_loss < best_loss:
            best_loss = val_loss
            no_improve = 0
            nlp.to_disk(output_dir)
            print(f"  ▶ Nouveau meilleur modèle sauvegardé (loss={best_loss:.3f})")
        else:
            no_improve += 1
            print(f"  Pas d'amélioration ({no_improve}/{patience})")
            if no_improve >= patience:
                print("Early stopping déclenché.")
                break

print("\nChargement du meilleur modèle pour test:")
nlp_best = spacy.load(output_dir)

test_samples = [ ] # Test Sample (Confidential)

for text in test_samples:
    doc = nlp_best(text)
    print(f"\nTexte : {text[:100]}...")
    for ent in doc.ents:
        print(f"  ➤ {ent.label_}: {ent.text}")

print(f"\nModèle sauvegardé dans : {output_dir.resolve()}")
