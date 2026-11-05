# Changelog

The current version is `metadata.version` in `skill-picker/SKILL.md`. Every version is tagged
`vX.Y.Z` in git and published as a GitHub release with its own `.skill` archive. Versions are
numbered MAJOR.MINOR.PATCH.

- **PATCH** (1.0.1) is a fix or clearer wording. The skill behaves the same.
- **MINOR** (1.1.0) is a new or changed rule, a catalog entry or a layout check feature.
- **MAJOR** (2.0.0) changes the install layout, the coverage table or how the skill works with
  the owner.

## [1.1.0] - 2026-11-06

### Changed

- The description says what the skill does and when to use it, without retelling the steps of
  the work. With the steps in the description, the model can follow them and skip the body of the
  skill, as Superpowers' tests showed. The trigger phrases are unchanged.

## [1.0.0] - 2026-11-06

The first numbered version.

### Added

- The version number in `SKILL.md`.

### Changed

- The description is cut from 1,239 to 950 characters to fit the Agent Skills limit of 1,024.
  Packaging and uploads to claude.ai refused the longer one. The list of layers in parentheses,
  the "update the coverage table" phrase and two qualifiers are gone. The other trigger phrases
  stay.

## Before 1.0.0

- **2026-10-25.** First version. Pick, vet and install the agent skills a project's stack needs
  (`101685a`).
