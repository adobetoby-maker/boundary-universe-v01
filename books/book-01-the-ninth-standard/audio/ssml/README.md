# GOOGLE SSML AUTHORING RULES

Google SSML is a production derivative of the canonical manuscript.

## Default pattern

```xml
<speak>
  <p>Normal narration.</p>
  <break time="350ms"/>
  <p>Next beat.</p>
</speak>
```

## Use sparingly

- `<break>` for deliberate dramatic beats, typically 150–650 ms.
- `<say-as>` for ambiguous numerals only when the engine misreads them.
- `<sub alias="...">` for stable pronunciation workarounds when needed.
- `<prosody>` only for subtle local corrections; do not globally over-direct pitch/rate.

## Performance policy

Narrator: contemporary American male, cinematic restraint, moderate pace. Kade is quick/dry; Darius is blunt and grounded; Ms. Alvarez is calm and precise; institutional voices are controlled rather than villainous.

As tension rises, use prose rhythm first and markup second.

Do not insert sound effects or multi-voice casting into the core audiobook track.
