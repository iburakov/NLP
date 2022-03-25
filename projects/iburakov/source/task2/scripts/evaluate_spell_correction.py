import pandas as pd
from pandas import DataFrame

from dirs import corrupted_dataset_dir, annotated_corpus_dir
from task1.newsgroup_message import read_newsgroup_message
from task1.tokenizer import tokenize_text
from task1.utils import read_tokens_from_annotated_corpus_tsv
from task2.sequence_alignment import get_optimal_alignment_hirschberg
from task2.spell_correction import correct_misspelled_tokens

_DEBUG_PRINTING = False


def _compare_token_sequences(real: DataFrame, fixed: DataFrame):
    alignment = get_optimal_alignment_hirschberg(real.token.values, fixed.token.values)
    alignment_df = DataFrame(alignment, columns=["src", "dest"])

    real_token_count = real.token.unique().size
    matched_token_count = alignment_df[alignment_df.src == alignment_df.dest].src.unique().size

    return real_token_count, matched_token_count, alignment_df


if __name__ == '__main__':
    pd.set_option('display.max_rows', 1000)
    pd.set_option('display.max_columns', 5)
    pd.set_option('expand_frame_repr', False)

    files = list(corrupted_dataset_dir.glob("*/*"))
    print(f"Files found: {len(files)}")

    total_real_token_count = 0
    total_corrupted_token_count = 0
    total_fixed_token_count = 0

    for i, filepath in enumerate(files):
        *_, category, doc_id = filepath.parts
        original_filepath = annotated_corpus_dir / "test" / category / f"{doc_id}.tsv"

        original_tokens = read_tokens_from_annotated_corpus_tsv(original_filepath)
        corrupted_tokens = tokenize_text(read_newsgroup_message(filepath).body)
        fixed_tokens = correct_misspelled_tokens(corrupted_tokens)

        real_token_count, corrupted_match_count, corrupted_alignment = \
            _compare_token_sequences(original_tokens, corrupted_tokens)
        _, fixed_match_count, fixed_alignment = _compare_token_sequences(original_tokens, fixed_tokens)

        if _DEBUG_PRINTING:
            comparison_df = DataFrame({"real": fixed_alignment.src,
                                       "corrupted": corrupted_tokens.token,
                                       "fixed": fixed_alignment.dest})
            comparison_df["match"] = comparison_df.real == comparison_df.fixed
            print(comparison_df)

        total_real_token_count += real_token_count
        total_corrupted_token_count += corrupted_match_count
        total_fixed_token_count += fixed_match_count

        if _DEBUG_PRINTING:
            print(f"Real:               {real_token_count}")
            print(f"Corrupted matched:  {corrupted_match_count}")
            print(f"Fixed matched:      {fixed_match_count}")

        current_scores = (total_corrupted_token_count / total_real_token_count,
                          total_fixed_token_count / total_real_token_count)

        print(f"Score: {current_scores[0] * 100:.2f}% -> {current_scores[1] * 100:.2f}%")
