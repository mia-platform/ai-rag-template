# date
ifeq (Darwin, $(shell uname))
	CURRENT_DATE = $(shell date -u +%d-%m-%Y)
else
	CURRENT_DATE = $(shell date -u -I)
endif

# dockerfile
VERSION_REGEX = eu\.mia-platform\.version="([^"]+)"
DOCKERFILE_NAME = Dockerfile
DOCKERFILE_CONTENT = `cat $(DOCKERFILE_NAME)`
DOCKERFILE_VERSION = "$(DOCKERFILE_CONTENT)" | sed -nE 's/.*$(VERSION_REGEX).*/\1/p'

# service
SERVICE_NAME = RAG-template
DOCKER_IMAGE_NAME = core/${SERVICE_NAME}

# service version
SV ?= patch
SEM_VERSION = ${SV}
MAJOR = $(shell echo $(DOCKERFILE_VERSION) | cut -d. -f1)
MINOR = $(shell echo $(DOCKERFILE_VERSION) | cut -d. -f2)
PATCH = $(shell echo $(DOCKERFILE_VERSION) | cut -d. -f3)

ifeq ($(SEM_VERSION), patch)
	NEW_SERVICE_VERSION := $(MAJOR).$(MINOR).$(shell expr $(PATCH) + 1)
else ifeq ($(SEM_VERSION), minor)
	NEW_SERVICE_VERSION := $(MAJOR).$(shell expr $(MINOR) + 1).0
else ifeq ($(SEM_VERSION), major)
	NEW_SERVICE_VERSION := $(shell expr $(MAJOR) + 1).0.0
endif

# coverage
COVERAGE_DIR = .coverage
COVERAGE_DATA_FILE = ${COVERAGE_DIR}/data
COVERAGE_HTML_DIR = $(COVERAGE_DIR)/html
COVERAGE_XML_FILE = ${COVERAGE_DIR}/xml

# badge
BADGES_DIR = .badges
COVERAGE_BADGE_FILE = ${BADGES_DIR}/coverage-badge.svg

# configurations
CONFIGURATION_PATH = src/configurations
CONFIGURATION_SCHEMA = service_config.json
CONFIGURATION_MODEL = service_model.py

install:
	uv sync

clear-deps:
	rm -rf .venv uv.lock

start:
	uv run dotenv -f local.env run -- python -m src.app

lint:
	uv run ruff check src tests

lint-fix:
	uv run ruff check --fix --unsafe-fixes src tests
	uv run ruff format src tests

test:
	uv run pytest -v tests

security-check:
	uv run bandit -r -l ./src

snapshot:
	uv run pytest -v --snapshot-update

coverage:
	uv run coverage run --data-file ${COVERAGE_DATA_FILE} --source=src -m pytest tests
	uv run coverage html --data-file ${COVERAGE_DATA_FILE} -d ${COVERAGE_HTML_DIR}
	uv run coverage xml --data-file ${COVERAGE_DATA_FILE} -o ${COVERAGE_XML_FILE}
	uv run genbadge coverage -i ${COVERAGE_XML_FILE} -o ${COVERAGE_BADGE_FILE}

# make update-version SV=<patch | minor | major>
update-version:
	@if [ -z "${NEW_SERVICE_VERSION}" ]; then\
		echo "Error: NEW_SERVICE_VERSION variable is empty.";\
		echo "\t- Ensure that the executed command includes the SV (semantic version) parameter.";\
		echo "\t- Ensure that the SV parameter value is supported ('patch', 'minor', 'major').";\
		echo "\t- Ensure that your Docker image file is named 'Dockerfile'.";\
		echo "\t- Ensure that your Docker image has the service version set in the 'eu.mia-platform.version' variable.";\
		echo "\t- Ensure that the value of the 'eu.mia-platform.version' variable in your Docker image follows semantic versioning (major.minor.patch).";\
		exit 1; \
	fi

	# update changelog
	@sed -i.bck "s|## Unreleased|## Unreleased\n\n## ${NEW_SERVICE_VERSION} - ${CURRENT_DATE}|g" "CHANGELOG.md"
	# update dockerfile
	@sed -i.bck "s|eu\.mia-platform\.version=\"[0-9]*.[0-9]*.[0-9]*.*\"|eu\.mia-platform\.version=\"${NEW_SERVICE_VERSION}\"|" "Dockerfile"
	# update src/app.py
	@sed -i.bck "s|version=\"[0-9]*.[0-9]*.[0-9]*.*\"|version=\"${NEW_SERVICE_VERSION}\"|" "src/app.py"
	# house cleaning
	@rm -fr "CHANGELOG.md.bck" "Dockerfile.bck" "src/app.py.bck"

	@git add "CHANGELOG.md" "Dockerfile" "src/app.py"
	@git commit -m "upgrade: service v${NEW_SERVICE_VERSION}"
	@git tag v${NEW_SERVICE_VERSION}


build-service-config:
	uv run datamodel-codegen \
	--input ${CONFIGURATION_PATH}/${CONFIGURATION_SCHEMA} \
	--input-file-type jsonschema \
	--output ${CONFIGURATION_PATH}/${CONFIGURATION_MODEL} \
	--use-title-as-name \
	--output-model-type pydantic_v2.BaseModel \
	--set-default-enum-member
