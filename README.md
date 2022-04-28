# BabyRobotGym
An OpenAI Gym Environment for Baby Robot


To get up and running with this simple custom Gym Environment, do the following:

* <i>git clone https://github.com/WhatIThinkAbout/BabyRobotGym.git</i>
* <i>cd BabyRobotGym</i>


Create a Conda environment to make sure you have the required packages:

<i>
  * conda create - name BabyRobotGym
  * conda activate BabyRobotGym
</i>
  
(when you're finished playing with this environment run "<i>conda deactivate</i>" to get back out)


Run the <i>setup.py</i> and <i>environment.yml</i> files, which install Gym, the BabyRobot environment and all the required packages into your new environment:

<i>pip install -e . </i>

Add this Conda environment as a Jupyter Notebook kernel:

<i>python -m ipykernel install - user - name=BabyRobotGym</i>

To open the test notebook, run "<i>jupyter notebook</i>", choose "<i>baby_robot_gym_test.ipynb</i>" and then select "<i>BabyRobotGym</i>" from the <i>Kernel</i> menu. Then prepare to be wowed! (well not really, as all it does is show the environment loads and that there are no errors!)