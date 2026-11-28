# Automata Mono build. Works with the GNU Make 3.81 that ships with macOS.

SHELL := /bin/bash
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:

FONTFORGE ?= fontforge
TTFAUTOHINT ?= ttfautohint
UV ?= uv

# Pinned upstream revisions. Existing checkouts must match; see `make sources`.
ROBOTO_DIR := RobotoMono
ROBOTO_URL := https://github.com/googlefonts/RobotoMono.git
ROBOTO_REV := 7bf0b33178844cc7d0c9915b746ece1be7f46bea
LIGATURIZER_DIR := Ligaturizer
LIGATURIZER_URL := https://github.com/ToxicFrog/Ligaturizer.git
LIGATURIZER_REV := c4065187a544a8fab40826fc91db1c6180a2d342
# Fira Code v3.1, the fonts/fira submodule commit recorded by LIGATURIZER_REV.
FIRA_REV := e9943d2d631a4558613d7a77c58ed1d3cb790992

BUILD_DIR := build
OUTPUT_DIR := fonts

# Keep in sync with STYLES and FIRA_WEIGHTS in scripts/config.py.
STYLES := Thin ThinItalic Light LightItalic Regular Italic Medium MediumItalic Bold BoldItalic
FIRA_WEIGHTS := Light Regular Medium SemiBold

FIRA_DIR := $(LIGATURIZER_DIR)/fonts/fira
UPSTREAM_FONTS := $(STYLES:%=$(ROBOTO_DIR)/fonts/ttf/RobotoMono-%.ttf)
FIRA_FONTS := $(FIRA_WEIGHTS:%=$(FIRA_DIR)/distr/otf/FiraCode-%.otf)
LIGATURIZER_SCRIPTS := $(addprefix $(LIGATURIZER_DIR)/,ligaturize.py ligatures.py char_dict.py)
BUILD_SCRIPTS := scripts/build_font.py scripts/config.py scripts/fira_ligatures.py \
	$(wildcard scripts/customizations/*.py)
FINAL_FONTS := $(STYLES:%=$(OUTPUT_DIR)/AutomataMono-%.ttf)
FONTFORGE_FONTS := $(STYLES:%=$(BUILD_DIR)/AutomataMono-%.fontforge.ttf)
MANIFESTS := $(STYLES:%=$(BUILD_DIR)/AutomataMono-%.json)
LICENSES := $(OUTPUT_DIR)/OFL-Roboto-Mono.txt $(OUTPUT_DIR)/OFL-Fira-Code.txt

# Known FontForge noise: upstream glyph name quirks, Fira Code's name table and
# DSIG, and Ligaturizer's ignore rules.
FONTFORGE_NOISE := sed -E \
	-e "/^Core python package 'pkg_resources' not found: Cannot discover plugins$$/d" \
	-e '/^This contextual rule applies no lookups\.$$/d' \
	-e '/^The glyph named [A-Za-z]+ is mapped to U\+[0-9A-F]+\.$$/d' \
	-e '/^But its name indicates it should be mapped to U\+[0-9A-F]+\.$$/d' \
	-e '/^The following table\(s\) in the font have been ignored by FontForge$$/d' \
	-e "/^  Ignoring 'DSIG' digital signature table$$/d" \
	-e "/^Warning: Mac (string is a subset of the Windows string in|and Windows entries in) the 'name' table/d" \
	-e '/^ (for the Family string in|SubFamily string in) the( English \(US\))? language/d' \
	-e '/^ ?(Mac|Windows) String: /d'

.PHONY: all build check proof sources verify-sources deps clean

all: check

build: $(FINAL_FONTS) $(LICENSES)

check: build $(MANIFESTS)
	$(UV) run --locked python scripts/validate.py --roboto-dir "$(ROBOTO_DIR)" \
		--ligaturizer-dir "$(LIGATURIZER_DIR)" --build-dir "$(BUILD_DIR)" --output-dir "$(OUTPUT_DIR)"

proof: build
	$(UV) run --locked python scripts/proof.py --roboto-dir "$(ROBOTO_DIR)" \
		--fonts-dir "$(OUTPUT_DIR)" --output-dir "$(BUILD_DIR)/proof"

deps:
	@command -v "$(FONTFORGE)" >/dev/null || { echo "Install FontForge: brew install fontforge" >&2; exit 1; }
	@command -v "$(TTFAUTOHINT)" >/dev/null || { echo "Install ttfautohint: brew install ttfautohint" >&2; exit 1; }
	@command -v "$(UV)" >/dev/null || { echo "Install uv: https://docs.astral.sh/uv/" >&2; exit 1; }

# Fetch exactly one commit into a temporary directory, then move it into place.
define fetch
rm -rf "$(1).tmp"
git init -q "$(1).tmp"
git -C "$(1).tmp" fetch -q --depth 1 "$(2)" "$(3)"
git -C "$(1).tmp" checkout -q --detach FETCH_HEAD
endef

$(ROBOTO_DIR)/.git:
	$(call fetch,$(ROBOTO_DIR),$(ROBOTO_URL),$(ROBOTO_REV))
	mv "$(ROBOTO_DIR).tmp" "$(ROBOTO_DIR)"

$(LIGATURIZER_DIR)/.git:
	$(call fetch,$(LIGATURIZER_DIR),$(LIGATURIZER_URL),$(LIGATURIZER_REV))
	git -C "$(LIGATURIZER_DIR).tmp" submodule update -q --init --depth 1 fonts/fira
	mv "$(LIGATURIZER_DIR).tmp" "$(LIGATURIZER_DIR)"

sources: verify-sources

verify = test "$$(git -C "$(1)" rev-parse HEAD)" = "$(2)" || { \
	echo "$(1) is not at the pinned revision $(2)." >&2; \
	echo "Remove $(1) to fetch it again, or update the pin in the Makefile." >&2; exit 1; }

verify-sources: | $(ROBOTO_DIR)/.git $(LIGATURIZER_DIR)/.git
	@$(call verify,$(ROBOTO_DIR),$(ROBOTO_REV))
	@$(call verify,$(LIGATURIZER_DIR),$(LIGATURIZER_REV))
	@$(call verify,$(FIRA_DIR),$(FIRA_REV))

$(UPSTREAM_FONTS) $(ROBOTO_DIR)/OFL.txt: | $(ROBOTO_DIR)/.git
	@test -f "$@"

$(FIRA_FONTS) $(LIGATURIZER_SCRIPTS) $(FIRA_DIR)/LICENSE: | $(LIGATURIZER_DIR)/.git
	@test -f "$@"

$(OUTPUT_DIR):
	mkdir -p "$@"

# Keep intermediate FontForge outputs in build/ for inspection. Listing them
# explicitly avoids .SECONDARY, which loops infinitely in GNU Make 3.81 under
# -j when an existing target depends on a missing secondary prerequisite whose
# own prerequisite is still running.
$(FONTFORGE_FONTS) $(MANIFESTS):

# 1. FontForge: glyph customizations and ligatures, plus a manifest of changes.
$(BUILD_DIR)/AutomataMono-%.fontforge.ttf $(BUILD_DIR)/AutomataMono-%.json: \
		$(ROBOTO_DIR)/fonts/ttf/RobotoMono-%.ttf $(FIRA_FONTS) $(LIGATURIZER_SCRIPTS) $(BUILD_SCRIPTS) \
		| verify-sources deps
	set -o pipefail; $(FONTFORGE) -quiet -skippyfile -skippyplug -lang=py -script scripts/build_font.py \
		--style "$*" --roboto-dir "$(ROBOTO_DIR)" --ligaturizer-dir "$(LIGATURIZER_DIR)" \
		--output "$(BUILD_DIR)/AutomataMono-$*.fontforge.ttf" --manifest "$(BUILD_DIR)/AutomataMono-$*.json" \
		2>&1 | $(FONTFORGE_NOISE)

# 2. fontTools: names and metadata. 3. ttfautohint: hinting.
$(OUTPUT_DIR)/AutomataMono-%.ttf: $(BUILD_DIR)/AutomataMono-%.fontforge.ttf $(BUILD_DIR)/AutomataMono-%.json \
		scripts/finalize.py scripts/config.py pyproject.toml uv.lock | deps $(OUTPUT_DIR)
	$(UV) run --locked python scripts/finalize.py --manifest "$(BUILD_DIR)/AutomataMono-$*.json" \
		--input "$<" --output "$(BUILD_DIR)/AutomataMono-$*.unhinted.ttf"
	$(TTFAUTOHINT) "$(BUILD_DIR)/AutomataMono-$*.unhinted.ttf" "$@"

$(OUTPUT_DIR)/OFL-Roboto-Mono.txt: $(ROBOTO_DIR)/OFL.txt | $(OUTPUT_DIR)
	cp "$<" "$@"

$(OUTPUT_DIR)/OFL-Fira-Code.txt: $(FIRA_DIR)/LICENSE | $(OUTPUT_DIR)
	cp "$<" "$@"

clean:
	rm -rf "$(BUILD_DIR)"
	rm -f $(FINAL_FONTS) $(LICENSES)
