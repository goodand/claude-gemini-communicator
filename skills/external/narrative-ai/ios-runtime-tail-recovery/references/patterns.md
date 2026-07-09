# Patterns

## Safe recovery order

1. Confirm current screen
2. Confirm current recording process
3. Reuse current state if valuable
4. Run the smallest missing tail
5. Capture screenshot/JUnit proof immediately

## When to split

Split the flow when:
- one CTA is flaky
- one selected card is unstable
- report is already proven but result is not
- mypage is still missing and can be proven independently

## When not to split

Do not split if:
- nothing useful has been captured yet
- login has not completed
- the recording artifact is already broken
