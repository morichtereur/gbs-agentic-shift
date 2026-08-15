.PHONY: install fetch classify analyze dashboard eval test all

install:  ; pip install -r requirements.txt
fetch:    ; python -m src.fetch
classify: ; python -m src.classify
analyze:  ; python -m src.analyze
dashboard:; python -m src.dashboard
eval:     ; python -m eval.eval_classify
test:     ; python -m pytest tests/ -q

all: fetch classify analyze dashboard
	@echo "Done. See RESULTS.md and dashboard.html"
