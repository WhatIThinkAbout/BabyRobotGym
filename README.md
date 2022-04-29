# BabyRobotGym
An OpenAI Gym Environment for Baby Robot


To get up and running with this simple custom Gym Environment, do the following:

## 1. Get the code:

* <i>git clone https://github.com/WhatIThinkAbout/BabyRobotGym.git</i>
* <i>cd BabyRobotGym</i>


## 2. Create a Conda environment and install the required packages:

### On Unix:

* <i>conda env create -f environment_unix.yml</i>

### On Windows:

* <i>conda env create -f environment_windows.yml</i>


## 3. Activate the environment:

* <i>conda activate BabyRobotGym</i>
  
(when you're finished playing with this environment run "<i>conda deactivate</i>" to get back out)


## 4. Run the test notebook:

* From the activated environment run "<i>jupyter notebook</i>" and choose "<i>baby_robot_gym_test.ipynb</i>" 
* Alternatively, open "<i>baby_robot_gym_test.ipynb</i>" in VS Code and make sure to choose "<i>BabyRobotGym</i>" as the kernel.

(When running in jupyter notebook the current Conda environment will automatically be used and the required packages should all be available. It's also possible to run "<i>python -m ipykernel install --user --name=BabyRobotGym</i>" which will create a Jupyter Notebook kernel, that can then be selected from the notebook's menu.)


## 5. Be amazed!

(well not really, as all it does is show the environment loads and that there are no errors!)