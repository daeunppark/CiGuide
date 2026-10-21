# Current Slide Notes

## Project and table
Chosen primitive: private-key encryption. The original table is Lecture 6 PDF p. 27. Rows 1–3 are instantiated as CBC with PKCS#7 and HMAC-SHA256 in an independent-key Encrypt-then-MAC composition. GCM/CCM are added rows. Added columns are Freshness Check, Storage Complexity — Output, Time Complexity, Message Length Required in Advance, Integrated Authentication and Parallel Encryption. See comparison_table.md and sources.md.

## Adaptive filtering
Expected candidate reduction = 0.5 × (current candidates − candidates after Yes), with equal Yes/No prior. No means not required; IDK preserves candidates. Ties use question-list order. Recalculate after each answer. Initially Q2 and Q3 both score 2; Q2 comes first. After Q2 No/unknown, Q3 is next. Q7/Q8 can also filter based on explicit user preferences. Q4 storage is inactive without a byte limit.

## Accessible questions
All prompts offer Yes / No / I don’t know. The first unknown displays a plain-English example and repeats the question. A second unknown advances without guessing. Unknown and unasked items remain unconfirmed. The permanently inactive Storage question is omitted from the result’s Not assessed list.

## Final ranking
If filtering leaves multiple candidates, ask useful differing preferences. Rank question priority is balanced property splits, with list-order tie breaking. A matching Yes earns one point. No/IDK adds zero points. Candidates are never removed in this phase. Equal scores share a rank; tied display order has no meaning. This is a preference ranking, not a security or speed ranking. One candidate skips this phase.

## Browser and CLI
Find My Scheme | Comparison Table | Decision Tree | Evaluation | Sources. The browser works offline with no backend. Python supplies standard input/output. Both use the same data and are verified for matching outputs. The tree shows filtering and ranking branches. Source inputs are data/*.csv and data/*.json; build with python3 run.py build after changes.

## Evaluation
Uniformly sample a target; answer all questions consistently with its features; pass if the target appears anywhere in the final ranked list. Default: 10,000 trials, seed 6903. Choice correctness: 100.00%. This is inclusion, not unique identification. No IDK is simulated in the base experiment. The Evaluation tab shows this primary metric and Expected/Actual cases only. Raw reports keep secondary diagnostics. Inclusion is not directly comparable to a single random choice.

## Current questions and examples

### Q1
Should the receiver be able to tell if someone changed your message?

IDK example: You send “Send $10,” but someone changes it to “Send $100” before it arrives. Should the receiver be able to notice that the message was changed?

### Q2
Does the receiver need to check if your message was sent recently?

IDK example: You send a door-unlock command that should only be accepted for 30 seconds. Should the receiver check when it was sent and reject it if it is too old?

### Q3
Does your application need to encrypt different parts of a file at the same time?

IDK example: Encrypting means locking data so that only someone with the secret key can read it. Imagine a large file split into smaller parts. Some methods can lock several parts at once instead of one at a time. Does your application need this ability?

### Q4 (inactive: budget needed)
Does your application have a limit on the extra space used to store each encrypted message?

IDK example: An encrypted message may need extra information, such as a tag that helps detect changes. This takes up storage space. Does your application have a strict limit on that extra space?

### Q6
Does your application need to start encrypting before it knows the full message size?

IDK example: Your application receives data a little at a time and does not yet know how much will arrive. Does it need to start encrypting before all the data arrives?

### Q7
Would you like one method that both locks your message and checks if someone changed it?

IDK example: Think of sending a locked box with a seal. You want one method to lock the box and help the receiver notice if someone changed what was sent. Would you prefer one method that handles both jobs?

### Q8
If you do not need to check when a message was sent, would you prefer to skip that step?

IDK example: Your application does not care when a message was sent. Adding a timestamp means storing and checking the time too. Would you prefer to leave out that extra step?

### R1
Even if it is not required, would you prefer one method that both locks your message and checks for changes?

IDK example: Some options use one standard design for both jobs. Others combine an encryption method with a separate check. Would you prefer the first approach?

### R2
If checking the sending time is optional, would you prefer to leave out that extra step?

IDK example: A timestamp stores when a message was sent and makes the receiver check the time. If you do not need that check, would you prefer an option without it?

### R3
Even if it is not required, would you prefer to encrypt several parts of a file at once?

IDK example: Imagine a large file split into parts. Some methods can lock several parts at the same time. Would you prefer that ability, even if your application can work without it?

## Limits and remaining submission work
Storage budgets are not assessed. The filtering capability mapping supports this table schema, rather than arbitrary cryptographic features. Evaluation is synthetic; no user study or encryption implementation is claimed. A finished slide deck and 10–15 minute video recording remain to be produced.
