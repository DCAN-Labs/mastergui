**Launch Mastergui**
1. ssh to Rushmore with X enabled
2. Create a directory "masterguioutput" in your home directory.
3. ```cd /mnt/max/shared/code/internal/GUIs/mastergui```
4. Run the shell script go.sh
```./go.sh```
5. On the right of the splash screen, under "Create Analysis",  click "New MPlus".
6. Select the first template "Development Testing With Prompts" in the list on the left and click "Select Template" in the bottom right corner.
7. You will be taken to the "Input Data Review" tab.  It is time to select your non-imaging data from an Excel or CSV file. 
    * Click Browse on the right
    * navigate to select /mnt/max/shared/projects/mastergui/demo/Tutorial_Test_1a.csv
8. You may inspect your data on this tab but no further action is required.
9. Go to the next tab Model Builder.

**Simple Test, No Voxels**
10. Click on the entry under "Voxelized Columns" and click the minus sign below it to remove it.
11. Under Template Requirements Select values in the "output", "predictor", and "mediator" drop downs." [For example PGS, Sex, NewAge]
12. Click "Apply" under Template Requirements and note your generated MPlus model in the right tab.
13. Go to the execution tab and click Run Analysis. 
14. The results of your Mplus model should appear below. 

**Test With Voxel**
15. If you performed the Voxelized Column removal of step 10, now add it back.
    * on the Model Builder tab, click the "+" under the "Voxelized Columns" list. 
    * scroll down to select "PATH_HCP"
    * Give a column name for the generated voxel, suggested "VOXEL_HCP"
16. Change your choices under Template Requirements so that at one of them includes the generated column VOXEL_HCP.
    * For example, Outcome: VOXEL_HCP, Predictor: PGS, Mediator: Sex
17. On the Analysis tab click Test Analysis to try it first with just a small number of voxels. 
18. After this completes, go to the Output Value Selector.
19. Scroll through one of the output files and click checkmarks next to the columns that you want to be extracted by the full analysis.
20. Go back to the Output tab and click "Run Analysis".  
    * Expect this step to take approximately 20 minutes, but you will get more specific time estimates the the output pane below as it proceeds.
    


