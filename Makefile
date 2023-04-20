sgr0 := $(shell tput sgr0)
bold := $(shell tput bold)
orange := $(shell tput setaf 166)

.PHONY: deploy destroy

deploy:
	@./setenv.sh
	@echo "$(bold)$(orange)AWS_PROFILE_SRC:$(sgr0) $${AWS_PROFILE_SRC}"
	@echo "$(bold)$(orange)AWS_PROFILE_TRG:$(sgr0) $${AWS_PROFILE_TRG}"
	@read -p "Do you want to deploy? (yes/no): " choice; \
	case "$$choice" in \
		yes|y) \
			echo "Deploy started."; \
			cdk deploy source --profile $${AWS_PROFILE_SRC} --require-approval never; \
			cdk deploy target --profile $${AWS_PROFILE_TRG} --require-approval never; \
			;; \
		no|n) \
			echo "Deploy cancelled."; \
			;; \
		*) \
			echo "Invalid choice. Deploy cancelled."; \
			;; \
	esac \
	
destroy:
	@./setenv.sh
	@echo "$(bold)$(orange)AWS_PROFILE_SRC:$(sgr0) $${AWS_PROFILE_SRC}"
	@echo "$(bold)$(orange)AWS_PROFILE_TRG:$(sgr0) $${AWS_PROFILE_TRG}"
	@read -p "Do you want to destroy? (yes/no): " choice; \
	case "$$choice" in \
		yes|y) \
			echo "Destroy started."; \
			cdk destroy source --profile $${AWS_PROFILE_SRC} --force; \
			cdk destroy target --profile $${AWS_PROFILE_TRG} --force; \
			;; \
		no|n) \
			echo "Destroy cancelled."; \
			;; \
		*) \
			echo "Invalid choice. Destroy cancelled."; \
			;; \
	esac \