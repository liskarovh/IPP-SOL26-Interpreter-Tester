# RT54 spec-focused suite

This suite is intentionally built around the SOL26 rules for instance attributes, especially:

1. A one-argument selector can create/update an instance attribute when the receiver does not already understand that one-argument message.
2. Creation must fail with 54 when reading the would-be attribute would collide with an existing zero-argument instance method.
3. For attribute access, `self` and `super` are mostly synonyms, but their method-collision checks differ:
   - `self` considers methods in the receiver's own class.
   - `super` considers only the parent chain.
4. A parent method may create an attribute that is later hidden by a child zero-argument method; `super` must still be able to read the attribute.
5. Unknown one-argument keywords on ordinary objects are attribute writes, not 51.
6. Unknown multi-keyword selectors are not attribute writes and should still become 51.

The suite is designed to catch both bad directions:
- too strict 54 (rejecting parent-created hidden attributes)
- too lax 54 (allowing genuine collisions)
