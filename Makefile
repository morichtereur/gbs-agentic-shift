.PHONY: install fetch classify analyze dashboard eval gold-country eval-country test all

install:  ; pip install -r requirements.txt
fetch:    ; python -m src.fetch
classify: ; python -m src.classify
analyze:  ; python -m src.analyze
dashboard:; python -m src.dashboard
eval:     ; python -m eval.eval_classify
gold-country: ; python -m eval.build_country_gold_template
eval-country: ; python -m eval.eval_country
test:     ; python -m pytest tests/ -q

all: fetch classify analyze dashboard
	@echo "Done. See RESULTS.md and dashboard.html"
