![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# Tiny Tapeout Verilog Project Template

- [Read the documentation for project](docs/info.md)

## What is Tiny Tapeout?

Tiny Tapeout is an educational project that aims to make it easier and cheaper than ever to get your digital and analog designs manufactured on a real chip.

To learn more and get started, visit https://tinytapeout.com.

## Set up your Verilog project

1. Add your Verilog files to the `src` folder.
2. Edit the [info.yaml](info.yaml) and update information about your project, paying special attention to the `source_files` and `top_module` properties. If you are upgrading an existing Tiny Tapeout project, check out our [online info.yaml migration tool](https://tinytapeout.github.io/tt-yaml-upgrade-tool/).
3. Edit [docs/info.md](docs/info.md) and add a description of your project.
4. Adapt the testbench to your design. See [test/README.md](test/README.md) for more information.

The GitHub action will automatically build the ASIC files using [LibreLane](https://www.zerotoasiccourse.com/terminology/librelane/).

## Enable GitHub actions to build the results page

- [Enabling GitHub Pages](https://tinytapeout.com/faq/#my-github-action-is-failing-on-the-pages-part)

## Resources

- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
- [Join the community](https://tinytapeout.com/discord)
- [Build your design locally](https://www.tinytapeout.com/guides/local-hardening/)

## What next?

- [Submit your design to the next shuttle](https://app.tinytapeout.com/).
- Edit [this README](README.md) and explain your design, how it works, and how to test it.
- Share your project on your social network of choice:
  - LinkedIn [#tinytapeout](https://www.linkedin.com/search/results/content/?keywords=%23tinytapeout) [@TinyTapeout](https://www.linkedin.com/company/100708654/)
  - Mastodon [#tinytapeout](https://chaos.social/tags/tinytapeout) [@matthewvenn](https://chaos.social/@matthewvenn)
  - X (formerly Twitter) [#tinytapeout](https://twitter.com/hashtag/tinytapeout) [@tinytapeout](https://twitter.com/tinytapeout)
  - Bluesky [@tinytapeout.com](https://bsky.app/profile/tinytapeout.com)

## ADAMA-1 Plasticity Core — shuttle record

- **Shuttle:** Tiny Tapeout SKY 26e (lot CI-2612, closes 2026-11-30, chips expected 2027-05-12)
- **Tiles:** 1x1 (single 167x108 um tile)
- **PDK:** sky130A
- **Top module:** `tt_um_marzmmp_adama_plasticity`

What this die is, precisely: the **plasticity engine only** — LTP/LTD synaptic
update (`nmf_synapse_update`) and the circadian tick (`nmf_tick`) from the
ADAMA-1 neuromorphic core. It is not the memory fabric; the 144-ring fabric with
the MRU residency table is ~13.3k gates and needs far more than one tile.

Interface:
- `ui[3:0]` addr, `ui[6]` write/reset, `ui[7]` write-enable
- `uio[3:0]` write data (inputs), `uio[7:4]` live status: satur, floored, tick, wrapped
- `uo[7:0]` addressed readback byte (addr 5 returns the status nibble)

Source of truth is the private repo `marzmmp/adama-1-silicon`; this repository is
generated from it by `tools/sync_tt.sh`. Do not edit here by hand.
