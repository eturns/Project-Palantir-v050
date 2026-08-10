from math import comb


def resist_will_refund_distribution(
    paid_dice_count: int,
) -> dict[int, float]:
    if paid_dice_count < 0:
        raise ValueError(
            "Paid resistance dice count cannot be negative."
        )

    return {
        refund_count: (
            comb(paid_dice_count, refund_count)
            * (1 / 6) ** refund_count
            * (5 / 6) ** (
                paid_dice_count - refund_count
            )
        )
        for refund_count in range(
            paid_dice_count + 1
        )
    }