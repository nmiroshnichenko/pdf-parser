## pdf-parser.py
## Compare structure of PDF files (finding key-value pairs).
## Ignore content values — just their positioning.

import fitz
import sys
import math
from pprint import pprint

FONT_TOLERANCE = 0.5
POS_TOLERANCE = 1.5


def extract_structured_text(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]  # check only 1 page for now
    blocks = page.get_text("dict")["blocks"]

    structured = []
    prev_key = None
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not text:
                    continue

                pos = (round(span["bbox"][0], 1), round(span["bbox"][1], 1))
                font_size = round(span["size"], 2)

                entry = {
                    "text": text,
                    "pos": pos,
                    "font": font_size
                }

                # key or value?
                if ":" in text:
                    entry["type"] = "key"
                    prev_key = entry
                    structured.append(entry)
                elif prev_key and is_value_near(prev_key["pos"], pos):
                    entry["type"] = "value"
                    structured.append(entry)
                    prev_key = None
                else:
                    entry["type"] = "value"
                    structured.append(entry)

    return structured


def is_value_near(key_pos, val_pos):
    dx = abs(key_pos[0] - val_pos[0])
    dy = abs(key_pos[1] - val_pos[1])
    return dx < 100 and dy < 10


def match_elements(ref_data, cmp_data):
    matched = []
    unmatched = []
    used_cmp = set()

    for ref_item in ref_data:
        best_match = None
        best_dist = float("inf")

        for idx, cmp_item in enumerate(cmp_data):
            if idx in used_cmp:
                continue
            if ref_item["type"] != cmp_item["type"]:
                continue

            dist = math.dist(ref_item["pos"], cmp_item["pos"])
            if dist <= POS_TOLERANCE and abs(ref_item["font"] - cmp_item["font"]) <= FONT_TOLERANCE:
                if dist < best_dist:
                    best_match = (idx, cmp_item)
                    best_dist = dist

        if best_match:
            used_cmp.add(best_match[0])
            matched.append((ref_item, best_match[1]))
        else:
            unmatched.append(ref_item)

    return matched, unmatched


def calc_score(total, unmatched):
    if total == 0:
        return 0.0
    return round((total - unmatched) / total * 100, 2)


def print_comparison(ref_path, cmp_path):
    print(f"\nComparing: {ref_path} vs {cmp_path}\n")

    ref_struct = extract_structured_text(ref_path)
    cmp_struct = extract_structured_text(cmp_path)

    matched, missing = match_elements(ref_struct, cmp_struct)

    score = calc_score(len(ref_struct), len(missing))

    if missing:
        for item in missing:
            item_type = item["type"].capitalize()
            text = item["text"]
            x, y = item["pos"]
            font = item["font"]

            # Try to find if it's actually moved, not just missing
            moved_match = None
            for cmp_item in cmp_struct:
                if cmp_item["text"] == text and cmp_item["type"] == item["type"]:
                    dist = math.dist(item["pos"], cmp_item["pos"])
                    if dist > POS_TOLERANCE:
                        moved_match = cmp_item
                        break

            if moved_match:
                cmp_x, cmp_y = moved_match["pos"]
                cmp_font = moved_match["font"]
                print(f"  Moved → {item_type} text='{text}'")
                print(f"    ref: ({x:.3f}, {y:.3f}) font={font:.2f}  !=")
                print(f"    cmp: ({cmp_x:.3f}, {cmp_y:.3f}) font={cmp_font:.2f}")
            else:
                print(f"  Missing → {item_type} text='{text}'")
                print(f"    ref: ({x:.3f}, {y:.3f}) font={font:.2f}")

    print(f"Similarity = {score:.2f}%\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf-parser.py ref.pdf [other1.pdf other2.pdf ...]")
        sys.exit(1)

    ref_pdf = sys.argv[1]
    compare_with = sys.argv[2:]

    if not compare_with:
        print("WARN: Only ref file provided. Nothing to compare.")
        pprint(extract_structured_text(ref_pdf))
        sys.exit(0)

    for cmp_pdf in compare_with:
        print("========================")
        print_comparison(ref_pdf, cmp_pdf)
        # print("========================")
        # pprint(extract_structured_text(cmp_pdf))
