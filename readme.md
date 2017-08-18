# Haptic Brain Explorer

## To prepare

Checkout the omega python robot code in the root of this repo (it will be ignored by git by default). The folder must be named `omega_cpp_py`.
For example, in the root of the repository you can type

```
git clone https://github.com/florisvanvugt/omega_cpp_py.git
```

You will also need a brain image, for example you can download the MNI152 template [here](http://packages.bic.mni.mcgill.ca/mni-models/icbm152/mni_icbm152_nl_VI_nifti.zip).


## To run

```
make -C omega_cpp_py
python haptic_brain.py
```




## TODO

- [ ] Viscosity dependence on tissue type
- [ ] Allow larger window display
