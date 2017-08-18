
run: robot
	python hapticbrain.py

robot:
	make -C omega_cpp_py robot

kill:
	make -C omega_cpp_py kill
