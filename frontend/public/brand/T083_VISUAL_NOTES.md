## T083 Visual Notes

### Current repo asset strategy

The current repository ships three homepage brand visuals as handcrafted SVG concept scenes:

- `t083-hero-collaboration-scene.svg`
- `t083-review-pipeline-scene.svg`
- `t083-device-participation-scene.svg`

This fallback was chosen because no live image generation credential was available in the local environment during implementation.

### Intended generated-image direction

If we later replace the SVG concept scenes with raster-generated assets, keep the same three-scene structure:

1. Hero collaboration scene
   - Product brand illustration / composited concept visual
   - Developer command center + tester task flow + review checkpoints
   - Multi-platform beta workflow
   - Professional, product-facing, not stock-photo

2. Review pipeline supporting panel
   - Developer-side review board
   - Participation requests, qualification checks, task bridge
   - Operational clarity and decision support

3. Device participation supporting panel
   - Tester-side participation and task execution
   - Device profile, participation request, structured feedback
   - Cross-device context without literal UI screenshots

### Prompt baseline for future raster generation

#### Hero

Use case: stylized-concept
Asset type: landing page hero
Primary request: a polished product-brand illustration showing a developer workspace, tester participation, and structured review flowing through one coordinated beta collaboration platform
Scene/backdrop: floating interface surfaces in a clean product studio atmosphere
Subject: desktop dashboard, mobile tester device, review cards, task and feedback checkpoints
Style/medium: premium product illustration, composited concept visual, not stock photography
Composition/framing: wide hero composition with room for homepage copy on one side
Lighting/mood: calm, high-trust, professional, luminous
Color palette: cobalt blue, soft teal, warm amber, graphite, cloud white
Constraints: no text in the artwork, no logos, no watermark, avoid generic AI fantasy aesthetics

#### Review supporting panel

Use case: stylized-concept
Asset type: supporting homepage brand panel
Primary request: a product illustration of a review pipeline where participation requests, qualification checks, and task creation are visible as connected operational stages
Style/medium: crisp product brand illustration
Composition/framing: medium panel composition
Lighting/mood: focused, operational, trustworthy
Constraints: no text, no watermark, no stock-photo feeling

#### Tester supporting panel

Use case: stylized-concept
Asset type: supporting homepage brand panel
Primary request: a product illustration of tester participation across multiple devices with participation requests, assigned tasks, and feedback submission cues
Style/medium: premium product illustration
Composition/framing: medium panel composition
Lighting/mood: active, capable, collaborative
Constraints: no text, no watermark, no generic AI landing-page clutter
