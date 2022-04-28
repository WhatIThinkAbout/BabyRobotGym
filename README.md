# BabyRobotGym
An OpenAI Gym Environment for Baby Robot


To get up and running with this simple custom Gym Environment, do the following:

## 1. Get the code:

* <i>git clone https://github.com/WhatIThinkAbout/BabyRobotGym.git</i>
* <i>cd BabyRobotGym</i>


## 2. Create a Conda environment to hold the required packages:

* <i>conda create --name BabyRobotGym</i>
* <i>conda activate BabyRobotGym</i>
  
(when you're finished playing with this environment run "<i>conda deactivate</i>" to get back out)


## 3. Make sure you have the required packages in your new environment:

Run the <i>setup.py</i> and <i>environment.yml</i> files, which install Gym, the BabyRobot environment and all the required packages into your new environment:

* <i>pip install -e . </i>


## 4. Add this Conda environment as a Jupyter Notebook kernel:

* <i>python -m ipykernel install --user --name=BabyRobotGym</i>

## 5. Run the notebook:

To open the test notebook, run "<i>jupyter notebook</i>", choose "<i>baby_robot_gym_test.ipynb</i>" and then select "<i>BabyRobotGym</i>" from the <i>Kernel</i> menu. Alternatively open the project in VS Code and select the <i>BabyRobotGym</i> environment there.

Then prepare to be wowed! (well not really, as all it does is show the environment loads and that there are no errors!)