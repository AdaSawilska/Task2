#!/usr/bin/env python
# encoding: utf-8
import csv
import os
import sys

import numpy as np
import pandas as pd

from load_data import data, mice, phases

this = sys.modules[__name__]  # this is now your current namespace

# clears the file mice.csv and adds tittles
with open('./output/mice.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t')
    writer.writerow(
        ["mouse"] + ["phase"] + ["time in room1"] + ["time in room2"] + ["time in room3"] + ["time in room4"])

# Number of animals in experiment
print(list(mice))
print("Numer of mice: %s" % len(list(mice)))
# experiment phases
print(phases.sections())
# start, end of each phase (as Unix time - https://en.wikipedia.org/wiki/Unix_time)
phase_time = []
print("Range of phases")
for phase in phases.sections():
    phase_time.append(phases.gettime(phase))
    print(phases.gettime(phase))

# creates an empty list for each room {1,2,3,4}


for i in range(len(mice)):

    mouse = list(mice)[i]

    all_rooms = []
    all_start_times = []
    all_end_times = []

    global rest, previous_room
    for j in range(len(phases.sections())):
        for x in range(1, 5):
            setattr(this, 'room%s' % x, [])

        start_times = []
        end_times = []
        room_numbers = []


        phase = phases.sections()[j]
        phase_end_time = phase_time[j][1]
        #print(phase_end_time)

        # Visits of a mouse to the rooms during one phase can be accesed like that:
        data.unmask_data()
        data.mask_data(*phases.gettime(phase))
        # Because of masking only visits starting in the given phase are returned.

        #add the time which was oryginally in previous phase but time is from next
        if j>0 and rest!=0 and previous_room!=0:
            start_times.append(phase_time[j][0])
            end_times.append(phase_time[j][0]+rest)
            room_numbers.append(previous_room)
            rest = 0
            previous_room = 0


        start_times.extend(data.getstarttimes(mouse))
        end_times.extend(data.getendtimes(mouse))
        room_numbers.extend(data.getaddresses(mouse))






        # time spend in a room
        for change_of_room in range(len(room_numbers)):
            if end_times[change_of_room] > phase_end_time:
                rest = end_times[change_of_room] - phase_end_time
                end_times[change_of_room] = phase_end_time
                previous_room = room_numbers[change_of_room]
                print(end_times[change_of_room], room_numbers[change_of_room])


            if room_numbers[change_of_room] == 1:
                room1.append(end_times[change_of_room] - start_times[change_of_room])
            elif room_numbers[change_of_room] == 2:
                room2.append(end_times[change_of_room] - start_times[change_of_room])
            elif room_numbers[change_of_room] == 3:
                room3.append(end_times[change_of_room] - start_times[change_of_room])
            elif room_numbers[change_of_room] == 4:
                room4.append(end_times[change_of_room] - start_times[change_of_room])


        # for st, en, room in zip(start_times, end_times, room_numbers):
        #      print("visit to room %d, starting %f, ending %f, phase%s" % (room, st, en, phase))
        all_rooms.extend(room_numbers)
        all_start_times.extend(start_times)
        all_end_times.extend(end_times)

        time1 = sum(room1)
        time2 = sum(room2)
        time3 = sum(room3)
        time4 = sum(room4)

        #print("----------------")
        # writes down the data to csv file
        with open('./output/mice.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t')
            writer.writerow(
                [mouse] + [phase] + ["%.5f" % time1] + ["%.5f" % time2] + ["%.5f" % time3] + ["%.5f" % time4])


    csvfile.close()

    # save all mice behaviour into separate file
    mousearray = pd.DataFrame(list(zip(all_rooms, all_start_times, all_end_times)), columns=["Room", "Start", "End"])
    mousearray.to_csv('./output/miceDatasets/mouse%s.csv' % mouse, sep='\t')


# reads the data for every mouse to dataset
dataframes = []
dataframes_names = []
folder_path = './output/miceDatasets/'
folder_list = os.listdir(folder_path)
folder_list = np.array(folder_list)

for dataset in folder_list:
    url = folder_path + dataset
    dataframes.append(pd.read_csv(url, sep='\t', index_col=0))
    dataframes_names.append(dataset)

dataframes_names = [e.replace('.csv', '') for e in dataframes_names]
dataframes_names = [e[5:] for e in dataframes_names]


# function seraching if mice were in the same room together
def compare_datasets(data1, data2, name1, name2, phase_time, phase_names):
    # variable which increments the start row of second dataframe - if time is too low
    w = 0
    list_of_phase = []
    list_of_rooms = []
    list_of_sharetime = []
    list_of_mouse1 = []
    list_of_mouse2 = []

    #loop for first mouse in pair
    for x in data1.index:
        # loop describing which phase we consider
        for t in range(6):
            if data1.iat[x, 2] <= phase_time[t][1]:
                phase = phase_names[t]
                # print(phase)
                break
        #loop for second mouse in pair
        for y in range(w, len(data2)):
            #conditions which describes if the time was shared in one room
            if data1.iat[x, 1] <= data2.iat[y, 1] and data1.iat[x, 0] == data2.iat[y, 0] and data1.iat[x, 2] >= data2.iat[y, 2] :
                sharetime = data2.iat[y, 2] - data2.iat[y, 1]
                #print(x, y, "time: %s" % sharetime, data1.iat[x, 0], phase)
                a=save(phase, data2.iat[y, 0], sharetime, name1, name2, list_of_phase, list_of_rooms, list_of_sharetime, list_of_mouse1, list_of_mouse2)

            elif data1.iat[x, 1] >= data2.iat[y, 1] and data1.iat[x, 0] == data2.iat[y, 0] and data1.iat[x, 2] >= data2.iat[y, 2] and data1.iat[x, 1] < data2.iat[y, 2]:
                sharetime = data2.iat[y, 2] - data1.iat[x, 1]
                #print(x, y, "time: %s" % sharetime, data1.iat[x, 0], phase)
                a=save(phase, data2.iat[y, 0], sharetime, name1, name2, list_of_phase, list_of_rooms, list_of_sharetime,
                     list_of_mouse1, list_of_mouse2)

            elif data1.iat[x, 1] >= data2.iat[y, 1] and data1.iat[x, 0] == data2.iat[y, 0] and data1.iat[x, 2] <= data2.iat[y, 2]:
                sharetime = data1.iat[x, 2] - data1.iat[x, 1]
                #print(x, y, "time: %s" % sharetime, data1.iat[x, 0], phase)
                a=save(phase, data2.iat[y, 0], sharetime, name1, name2, list_of_phase, list_of_rooms, list_of_sharetime,
                     list_of_mouse1, list_of_mouse2)

            elif data1.iat[x, 1] <= data2.iat[y, 1] and data1.iat[x, 0] == data2.iat[y, 0] and data1.iat[x, 2] <= data2.iat[y, 2] and data1.iat[x, 2] > data2.iat[y, 1]:
                sharetime = data1.iat[x, 2] - data2.iat[y, 1]
                #print(x, y, "time: %s" % sharetime, data1.iat[x, 0], phase)
                a=save(phase, data2.iat[y, 0], sharetime, name1, name2, list_of_phase, list_of_rooms, list_of_sharetime,
                     list_of_mouse1, list_of_mouse2)
            elif data1.iat[x, 2] <= data2.iat[y, 1]:
                break

            elif data1.iat[x, 1] >= data2.iat[y, 2]:
                w = w +1
                continue
    return a

#function which saves data to lists and the dataframe
def save(phase, room, sharetime, name1, name2, list_of_phase, list_of_rooms, list_of_sharetime, list_of_mouse1, list_of_mouse2):
    list_of_phase.append(phase)
    list_of_rooms.append(room)
    list_of_sharetime.append(sharetime)
    list_of_mouse1.append(name1)
    list_of_mouse2.append(name2)
    mice_together_dataframes = list(zip(list_of_phase, list_of_rooms, list_of_sharetime, list_of_mouse1, list_of_mouse2))
    return mice_together_dataframes


#loop which chech the dependencies between mice
result = pd.DataFrame()
iterator = 1;
for m in range(0, len(mice)):
    for n in range(iterator, len(mice)):
        mice_together_dataframes = compare_datasets(dataframes[m], dataframes[n], dataframes_names[m],
                                                    dataframes_names[n], phase_time, phases.sections())
        df = pd.DataFrame(mice_together_dataframes, columns=["Phase", "Room", "Time", "Mouse One", "Mouse Two"])
        df = df.groupby(by=["Room", "Phase"]).agg(
            {'Phase': 'max', 'Room': 'max', 'Time': 'sum', 'Mouse One': 'max', 'Mouse Two': 'max'})
        df = df.reset_index(drop=True)
        result = result.append(df)
        print(m,n)

    iterator = iterator + 1


result = result.reset_index(drop=True)
result.to_csv('./output/mousepairs.csv', sep='\t')




