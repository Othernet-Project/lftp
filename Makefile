include conf/Makefile.in

COMPASS_PID = .compass_pid
COFFEE_PID = .coffee_pid

.PHONY: watch stop restart recompile

watch: $(COFFEE_PID) $(DEMO_COFFEE_PID)

stop:
	$(SCRIPTS)/coffee.sh stop $(COFFEE_PID)

restart: stop watch

recompile: 
	find $(JSDIR) -path $(JSDIR)/$(EXCLUDE) -prune -o -name "*.js" -exec rm {} +
	coffee --bare -c --output $(JSDIR) $(COFFEE_SRC)

$(COFFEE_PID): $(SCRIPTS)/coffee.sh
	$< start $@ $(COFFEE_SRC) $(JSDIR)
