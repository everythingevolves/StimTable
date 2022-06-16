# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 17:33:28 2019

@author: danielm
"""
import os, sys, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sync_py3 import Dataset

package_path = '/Users/danielm/Desktop/py_code/StimTable/'

def three_session_A_tables(exptpath):
    
    data = load_stim(exptpath)
    twop_frames, twop_vsync_fall, stim_vsync_fall, photodiode_rise = load_sync(exptpath)
    
    stim_table = {}
    stim_table['drifting_gratings'] = drifting_gratings_table(data, twop_frames)
    stim_table['natural_movie_1'] = natural_movie_1_table(data,twop_frames)
    stim_table['natural_movie_3'] = natural_movie_3_table(data,twop_frames)
    stim_table['spontaneous'] = get_spontaneous_table(data,twop_frames)
    
    return stim_table

def three_session_B_tables(exptpath):
    
    data = load_stim(exptpath)
    twop_frames, twop_vsync_fall, stim_vsync_fall, photodiode_rise = load_sync(exptpath)
    
    stim_table = {}
    stim_table['static_gratings'] = static_gratings_table(data, twop_frames)
    stim_table['natural_images'] = natural_images_table(data,twop_frames)
    stim_table['natural_movie_1'] = natural_movie_1_table(data,twop_frames)
    stim_table['spontaneous'] = get_spontaneous_table(data,twop_frames)
    
    return stim_table

def three_session_C_tables(exptpath):
    
    data = load_stim(exptpath)
    twop_frames, twop_vsync_fall, stim_vsync_fall, photodiode_rise = load_sync(exptpath)
    
    stim_table = {}
    stim_table['locally_sparse_noise_4deg'] = locally_sparse_noise_4deg_table(data, twop_frames)
    stim_table['locally_sparse_noise_8deg'] = locally_sparse_noise_8deg_table(data, twop_frames)
    stim_table['natural_movie_1'] = natural_movie_1_table(data,twop_frames)
    stim_table['natural_movie_2'] = natural_movie_2_table(data,twop_frames)
    stim_table['spontaneous'] = get_spontaneous_table(data,twop_frames)
    
    return stim_table

def VisualBehavior_NM1_table(exptpath,session_ID,frames_per_rep=900,num_reps=10):
    
    data = pd.read_pickle(exptpath+str(session_ID)+'_stim.pkl')
    twop_frames, stim_vsync_rise = load_sync_VB(exptpath+str(session_ID)+'_sync.h5')

    #36000 stim frames (600 seconds?)
    NM1_stim_frames = data['items']['behavior']['items']['fingerprint']['frame_indices']
    frame_in_movie = data['items']['behavior']['items']['fingerprint']['static_stimulus']['frame_list']
    
    print(NM1_stim_frames)
    print(len(stim_vsync_rise))
    
    start_frames = NM1_stim_frames
    start_frames[start_frames>=len(stim_vsync_rise)] = len(stim_vsync_rise) - 1
    
    whole_block_start_times = stim_vsync_rise[start_frames]
    
    first_NM1_frame = np.argwhere(frame_in_movie==0)[0,0]
    print('first frame: '+str(first_NM1_frame))
    
    start_time = np.zeros((num_reps*frames_per_rep,))
    end_time = np.zeros((num_reps*frames_per_rep,))
    NM1_frame_indices = np.zeros((num_reps*frames_per_rep,))
    frame_start_idx = first_NM1_frame
    for rep in range(num_reps):
        for NM1_frame_number in range(frames_per_rep):
            
            row = int(rep*frames_per_rep + NM1_frame_number)
            
            start_time[row] = whole_block_start_times[frame_start_idx]
            NM1_frame_indices[row] = NM1_frame_number
            
            next_frame_number = NM1_frame_number + 1
            if NM1_frame_number==(frames_per_rep-1):
                next_frame_number = 0
            
            #find range of stim frames during this NM1_frame presentation:
            if rep==(num_reps-1) and next_frame_number==0:
                median_frame_time = np.median(end_time - start_time)
                end_time[row] = start_time[row] + median_frame_time
            else:
                next_frame_idx = frame_start_idx + np.argwhere(frame_in_movie[frame_start_idx:]==next_frame_number)[0,0]
                end_time[row] = whole_block_start_times[next_frame_idx]
                
            frame_start_idx = next_frame_idx
    
    NM1_table = pd.DataFrame(np.column_stack((start_time,end_time,NM1_frame_indices)), columns=('Start_Time','End_Time','Frame'))
    
    return NM1_table

def load_sync_VB(syncpath,verbose=False,LONG_STIM_THRESH=0.2):
    
    d = Dataset(syncpath)
    
    if verbose:
        print(d.line_labels)
        
    vsync_2p_label = get_2p_vsync_line_label(d)
    vsync_stim_label = get_stim_vsync_line_label(d)
    photodiode_label = get_photodiode_line_label(d)

    # set the appropriate sample frequency
    sample_freq = d.meta_data['ni_daq']['counter_output_freq']

    # get sync timing for each channel
    twop_vsync_fall = d.get_falling_edges(vsync_2p_label) / sample_freq
    stim_vsync_fall = (
        d.get_falling_edges(vsync_stim_label)[1:] / sample_freq
    )  # eliminating the DAQ pulse
    photodiode_rise = d.get_rising_edges(photodiode_label) / sample_freq

    ptd_rise_diff = np.ediff1d(photodiode_rise)
    
    stim_vsync_rise = d.get_rising_edges(vsync_stim_label) / sample_freq
    if (stim_vsync_rise[1] - stim_vsync_rise[0]) > LONG_STIM_THRESH:
        stim_vsync_rise = stim_vsync_rise[1:]
    
    if verbose:
        plt.figure()
        plt.plot(photodiode_rise,np.zeros((len(photodiode_rise),)),'o')
        #plt.xlim(0,100)
        plt.show()
        
        plt.figure()
        plt.hist(ptd_rise_diff,range=[0,5])
        plt.show()

    # make sure all of the sync data are available
    channels = {
        'twop_vsync_fall': twop_vsync_fall,
        'stim_vsync_fall': stim_vsync_fall,
        'photodiode_rise': photodiode_rise,
    }
    channel_test = []
    for chan in list(channels.keys()):
        # Check that signal is high at least once in each channel.
        channel_test.append(any(channels[chan]))
        if not any(channels[chan]):
            print(chan+' is empty!')
    # if not all(channel_test):
    #     raise RuntimeError('Not all channels present. Sync test failed.')
    # elif verbose:
    #     print("All channels present.")

    # print(photodiode_rise)
    
    print('Num 2P vsync_falls: '+str(len(twop_vsync_fall)))
    print('Num photodiode_rises: '+str(len(photodiode_rise)))
    print('Num stimulus vsync_falls: '+str(len(stim_vsync_fall)))
    
    
    if channel_test[2]:
        
        # test and correct for photodiode transition errors
        ptd_rise_diff = np.ediff1d(photodiode_rise)
        short = np.where(np.logical_and(ptd_rise_diff > 0.1, ptd_rise_diff < 0.3))[
            0
        ]
        medium = np.where(np.logical_and(ptd_rise_diff > 0.5, ptd_rise_diff < 1.5))[
            0
        ]
        ptd_start = 3
        for i in medium:
            if set(range(i - 2, i)) <= set(short):
                ptd_start = i + 1
                
        if photodiode_rise.max() <= stim_vsync_fall.max():
            print('photodiode ends before stim_vsync already.')
            ptd_end = len(ptd_rise_diff)
        else:
            print('truncating photodiode to end before stim_vsync.')
            ptd_end = np.where(photodiode_rise > stim_vsync_fall.max())[0][0] - 1
        print('ptd_end: ' +str(ptd_end)+ ' max photodiode ' + str(photodiode_rise.max())+' max stim '+ str(stim_vsync_fall.max()))
    
    
        if ptd_start > 3 and verbose:
            print('ptd_start: ' + str(ptd_start))
            print("Photodiode events before stimulus start.  Deleted.")
    
        ptd_errors = []
        while any(ptd_rise_diff[ptd_start:ptd_end] < 1.8):
            error_frames = (
                np.where(ptd_rise_diff[ptd_start:ptd_end] < 1.8)[0] + ptd_start
            )
            print("Photodiode error detected. Number of frames:", len(error_frames))
            photodiode_rise = np.delete(photodiode_rise, error_frames[-1])
            ptd_errors.append(photodiode_rise[error_frames[-1]])
            ptd_end -= 1
            ptd_rise_diff = np.ediff1d(photodiode_rise)
    
        first_pulse = ptd_start
        stim_on_photodiode_idx = 60 + 120 * np.arange(0, ptd_end - ptd_start, 1)
    
        stim_on_photodiode = stim_vsync_fall[stim_on_photodiode_idx]
        photodiode_on = photodiode_rise[
            first_pulse + np.arange(0, ptd_end - ptd_start, 1)
        ]
        delay_rise = photodiode_on - stim_on_photodiode
    
        delay = np.mean(delay_rise[:-1])
        print("monitor delay: ", delay)
    else:
        delay = 0.01

    # adjust stimulus time to incorporate monitor delay
    stim_time = stim_vsync_fall + delay

    # convert stimulus frames into twop frames
    twop_frames = np.empty((len(stim_time), 1))
    for i in range(len(stim_time)):
        # crossings = np.nonzero(np.ediff1d(np.sign(twop_vsync_fall - stim_time[i]))>0)
        crossings = (
            np.searchsorted(twop_vsync_fall, stim_time[i], side='left') - 1
        )
        if crossings < (len(twop_vsync_fall) - 1):
            twop_frames[i] = crossings
        else:
            twop_frames[i : len(stim_time)] = np.NaN
            warnings.warn('Acquisition ends before stimulus.', RuntimeWarning)
            break

    return twop_frames, (stim_vsync_rise+delay)

def omFish_gratings_tables(exptpath,verbose=False):
    
    data = load_stim(exptpath)
    twop_frames, twop_vsync_fall, stim_vsync_fall, photodiode_rise = load_sync(exptpath)

    stim_table = {}  
    stim_table['drifting_gratings_contrast'] = drifting_gratings_table(data,twop_frames,stim_name='drifting_gratings_contrast')
    stim_table['drifting_gratings_TF'] = drifting_gratings_table(data,twop_frames,stim_name='drifting_gratings_TF')
    
    if verbose:
        count_sweeps_per_condition(stim_table['drifting_gratings_contrast'])
        count_sweeps_per_condition(stim_table['drifting_gratings_TF'])
    
    return stim_table

def SparseNoise_tables(exptpath):
    
    data = load_stim(exptpath)
    twop_frames, twop_vsync_fall, stim_vsync_fall, photodiode_rise = load_sync(exptpath)
    
    stim_table = {}
    stim_table['sparse_noise'] = sparse_noise_table(data, twop_frames)
    stim_table['spontaneous'] = get_spontaneous_table(data,twop_frames)
    
    return stim_table

def SizeByContrast_tables(exptpath,verbose=False):
    
    data = load_stim(exptpath)
    twop_frames, twop_vsync_fall, stim_vsync_fall, photodiode_rise = load_sync(exptpath)

    print_all_stim_types(data)

    stim_table = {}  
    stim_table['size_by_contrast'] = drifting_gratings_table(data,twop_frames,stim_name='size_by_contrast')
    stim_table['visual_behavior_flashes'] = visual_behavior_flashes_table(data,twop_frames)
    
    if verbose:
        count_sweeps_per_condition(stim_table['size_by_contrast'],columns=['SF','TF','Ori','Contrast','Size'])
        print(stim_table['size_by_contrast'])
        print(stim_table['visual_behavior_flashes'])
    
    return stim_table

def count_sweeps_per_condition(stim_table,columns=['SF','TF','Ori','Contrast']):

    num_sweeps = len(stim_table)    

    params = get_params(stim_table,columns)
        
    for combination in range(num_combinations(params)):
        
        combination_params = condition_combination_to_params(params,combination)
        
        print(combination_params)
        
        rows_in_condition = np.ones((num_sweeps,),dtype=np.bool)
        for i_col,column in enumerate(columns):
            rows_in_condition = rows_in_condition & (stim_table[column].values==combination_params[column])
            
        print(sum(rows_in_condition))
    print('Num blank sweeps: '+str(np.sum(stim_table['Ori'].isnull().values)))

def get_params(stim_table,columns):
    params = {}
    for c in columns:
        column_params = np.unique(stim_table[c].values)
        params[c] = column_params[np.isfinite(column_params)]
    return params

def num_combinations(params):
    num_combinations = 1
    for i_col,column in enumerate(list(params.keys())):
        num_combinations *= len(params[column])
    return num_combinations

def condition_combination_to_params(params,combination):
    
    columns = list(params.keys())
    
    combination_params = {}
    
    for i_col,column in enumerate(columns):
        
        divisor = 1
        columns_to_right = np.arange(i_col+1,len(columns))
        for j_col in columns_to_right:
            divisor *= len(params[columns[j_col]])
            
        modulo = num_combinations(params)
        columns_to_left = np.arange(0,i_col)
        for j_col in columns_to_left:
            modulo /= len(params[columns[j_col]])
        
        param_index = (int(combination) % int(modulo)) / int(divisor)
        combination_params[column] = params[column][int(param_index)]
    
    return combination_params

def coarse_mapping_create_stim_tables(exptpath):
    
    data = load_stim(exptpath)
    twop_frames, twop_vsync_fall, stim_vsync_fall, photodiode_rise = load_sync(exptpath)
    
    stim_table = {}
    stim_table['locally_sparse_noise'] = locally_sparse_noise_table(data,twop_frames)
    stim_table['drifting_gratings_grid'] = DGgrid_table(data,twop_frames)

    return stim_table
    
def lsnCS_create_stim_tables(exptpath):
    
    data = load_stim(exptpath)
    twop_frames, twop_vsync_fall, stim_vsync_fall, photodiode_rise = load_sync(exptpath)
    
    stim_table = {}
    stim_table['center_surround'] = center_surround_table(data,twop_frames)
    stim_table['locally_sparse_noise'] = locally_sparse_noise_table(data,twop_frames)
    
    return stim_table

def MovieClips_tables(exptpath,num_train_segments=5,num_test_segments=10,verbose=False):
    
    data = load_stim(exptpath)
    twop_frames, twop_vsync_fall, stim_vsync_fall, photodiode_rise = load_sync(exptpath)
    train_info = pd.read_pickle(package_path+'clip_info_train.pkl')
    test_info = pd.read_pickle(package_path+'clip_info_test.pkl')
    
    stim_table = {}
    for train_segment in range(num_train_segments):
        segment_name = 'clips_train_' + str(1+train_segment)
        stim_table[segment_name] = MovieClips_one_segment_table(data,twop_frames,segment_name,train_info)
        
    for test_segment in range(num_test_segments):
        segment_name = 'clips_test_' + str(1+test_segment) 
        stim_table[segment_name] = MovieClips_one_segment_table(data,twop_frames,segment_name,test_info)
    
    if verbose:
        print(stim_table)
    
    return stim_table

def MovieClips_one_segment_table(data,twop_frames,segment_name,info_df):
    
    segment_idx = get_stimulus_index(data,segment_name)
    stim_name = get_stim_name_for_segment(segment_name)

    is_stim = np.argwhere((info_df['stim_name'] == stim_name).values)[:,0]
    #clip_start_frames = info_df['start_frame'].values[is_stim]
    clip_end_frames = info_df['end_frame'].values[is_stim]
    num_clips = len(is_stim)
    
    timing_table = get_sweep_frames(data,segment_idx)
    num_segment_frames = len(timing_table)

    stim_table = init_table(twop_frames,timing_table)
    stim_table['stim_name'] = stim_name

    clip_number = -1 * np.ones((num_segment_frames,))
    frame_in_clip = -1 * np.ones((num_segment_frames,))
    curr_clip = 0
    curr_frame = 0
    for nf in range(num_segment_frames):
        if nf == clip_end_frames[curr_clip]:
            curr_clip += 1
            curr_frame = 0
            if curr_clip==num_clips:
                break
            
        clip_number[nf] = curr_clip
        frame_in_clip[nf] = curr_frame
        curr_frame += 1
            
    stim_table['clip_number'] = clip_number
    stim_table['frame_in_clip'] = frame_in_clip

    return stim_table

def get_stim_name_for_segment(segment_name):
    
    names = {'clips_train_1': 'PEsacc640_001_train',
             'clips_train_2': 'trn001lf_train',
             'clips_train_3': 'cont640_030lf_train',
             'clips_train_4': 'segmented_train',
             'clips_train_5': 'cont640_031lf_train',
             'clips_test_1': 'ds_warped_cont640_002lf_rep_test_0',
             'clips_test_2': 'ds_warped_segmented_test_0',
             'clips_test_3': 'ds_warped_cont640_002lf_rep_test_1',
             'clips_test_4': 'ds_warped_segmented_test_1',
             'clips_test_5': 'ds_warped_cont640_002lf_rep_test_2',
             'clips_test_6': 'ds_warped_segmented_test_2',
             'clips_test_7': 'ds_warped_cont640_002lf_rep_test_3',
             'clips_test_8': 'ds_warped_segmented_test_3',
             'clips_test_9': 'ds_warped_cont640_002lf_rep_test_4',
             'clips_test_10': 'ds_warped_segmented_test_4'
            }
    
    return names[segment_name]

def visual_behavior_flashes_table(data,twop_frames):
    
    stim_idx = get_stimulus_index(data,'visual_behavior_flashes')

    print_all_stim_attributes(data, stim_idx)
    
    timing_table = get_sweep_frames(data,stim_idx)
    
    stim_table = init_table(twop_frames,timing_table)
    stim_table['Image'] = data['stimuli'][stim_idx]['sweep_order'][:len(stim_table)]
    
    return stim_table

def drifting_gratings_table(data,twop_frames,stim_name='drifting_grating'):
    
    DG_idx = get_stimulus_index(data,stim_name)
    
    timing_table = get_sweep_frames(data,DG_idx)

    stim_table = init_table(twop_frames,timing_table)
    
    stim_attributes = data['stimuli'][DG_idx]['dimnames']
                       #  ['TF',
                       # 'SF',
                       # 'Contrast',
                       # 'Ori'
                       # ]
    
    for stim_attribute in stim_attributes:
        stim_table[stim_attribute] = get_attribute_by_sweep(data, DG_idx, stim_attribute)[:len(stim_table)]
    
    return stim_table

def static_gratings_table(data,twop_frames):
    
    SG_idx = get_stimulus_index(data,'static_grating')
    
    timing_table = get_sweep_frames(data,SG_idx)

    stim_table = init_table(twop_frames,timing_table)
    
    stim_attributes = ['SF',
                       'Contrast',
                       'Ori',
                       'Phase'
                       ]
    
    for stim_attribute in stim_attributes:
        stim_table[stim_attribute] = get_attribute_by_sweep(data, SG_idx, stim_attribute)[:len(stim_table)]
    
    return stim_table

def natural_images_table(data,twop_frames):
    
    ns_idx = get_stimulus_index(data,'natural_images')
    
    timing_table = get_sweep_frames(data,ns_idx)

    stim_table = init_table(twop_frames,timing_table)
    
    stim_table['Image'] = np.array(data['stimuli'][ns_idx]['sweep_order'][:len(stim_table)])

    return stim_table

def natural_movie_1_table(data,twop_frames):
    
    nm_idx = get_stimulus_index(data,'natural_movie_1')
    
    timing_table = get_sweep_frames(data,nm_idx)

    stim_table = init_table(twop_frames,timing_table)
    
    stim_table['Frame'] = np.array(data['stimuli'][nm_idx]['sweep_order'][:len(stim_table)])

    return stim_table

def natural_movie_2_table(data,twop_frames):
    
    nm_idx = get_stimulus_index(data,'natural_movie_2')
    
    timing_table = get_sweep_frames(data,nm_idx)

    stim_table = init_table(twop_frames,timing_table)
    
    stim_table['Frame'] = np.array(data['stimuli'][nm_idx]['sweep_order'][:len(stim_table)])

    return stim_table

def natural_movie_3_table(data,twop_frames):
    
    nm_idx = get_stimulus_index(data,'natural_movie_3')
    
    timing_table = get_sweep_frames(data,nm_idx)

    stim_table = init_table(twop_frames,timing_table)
    
    stim_table['Frame'] = np.array(data['stimuli'][nm_idx]['sweep_order'][:len(stim_table)])

    return stim_table

def locally_sparse_noise_4deg_table(data,twop_frames):
    
    lsn_idx = get_stimulus_index(data,'locally_sparse_noise_4deg')
    
    timing_table = get_sweep_frames(data,lsn_idx)

    stim_table = init_table(twop_frames,timing_table)
    
    stim_table['Frame'] = np.array(data['stimuli'][lsn_idx]['sweep_order'][:len(stim_table)])

    return stim_table

def locally_sparse_noise_8deg_table(data,twop_frames):
    
    lsn_idx = get_stimulus_index(data,'locally_sparse_noise_8deg')
    
    timing_table = get_sweep_frames(data,lsn_idx)

    stim_table = init_table(twop_frames,timing_table)
    
    stim_table['Frame'] = np.array(data['stimuli'][lsn_idx]['sweep_order'][:len(stim_table)])

    return stim_table

def sparse_noise_table(data,twop_frames):
    
    lsn_idx = get_stimulus_index(data,'sparse_noise')
    
    timing_table = get_sweep_frames(data,lsn_idx)

    stim_table = init_table(twop_frames,timing_table)
    
    stim_table['Frame'] = np.array(data['stimuli'][lsn_idx]['sweep_order'][:len(stim_table)])

    return stim_table

def locally_sparse_noise_table(data,twop_frames):
    
    lsn_idx = get_stimulus_index(data,'locally_sparse_noise')
    
    timing_table = get_sweep_frames(data,lsn_idx)

    stim_table = init_table(twop_frames,timing_table)
    
    stim_table['Frame'] = np.array(data['stimuli'][lsn_idx]['sweep_order'][:len(stim_table)])

    return stim_table

def get_spontaneous_table(data,twop_frames):
    
    MAX_SWEEPS = 50000
    MIN_DURATION = 2000
    start_frames = np.zeros((MAX_SWEEPS,))
    end_frames = np.zeros((MAX_SWEEPS,))
    
    curr_sweep = 0
    for i_stim, stim_data in enumerate(data['stimuli']):
        timing_table = get_sweep_frames(data,i_stim,verbose=False)
        stim_sweeps = len(timing_table)
        
        start_frames[curr_sweep:(curr_sweep+stim_sweeps)] = twop_frames[timing_table['start'],0]
        end_frames[curr_sweep:(curr_sweep+stim_sweeps)] = twop_frames[timing_table['end'],0]
        curr_sweep += stim_sweeps
        
    start_frames = start_frames[:curr_sweep]
    end_frames = end_frames[:curr_sweep]
    
    sort_idx = np.argsort(start_frames)
    start_frames = start_frames[sort_idx]
    end_frames = end_frames[sort_idx]
    
    intersweep_frames = start_frames[1:] - end_frames[:-1]
    spontaneous_blocks = np.argwhere(intersweep_frames>MIN_DURATION)[:,0]
    
    sp_start_frames = []
    sp_end_frames = []
    for sp_idx in spontaneous_blocks:
        sp_start_frames.append(end_frames[sp_idx])
        sp_end_frames.append(start_frames[sp_idx+1])
        
    sp_table = pd.DataFrame(np.column_stack((sp_start_frames,sp_end_frames)), columns=('Start', 'End'))

    return sp_table

def DGgrid_table(data,twop_frames):
    
    DG_idx = get_stimulus_index(data,'grating')
    
    timing_table = get_sweep_frames(data,DG_idx)

    stim_table = init_table(twop_frames,timing_table)
    
    stim_attributes = ['TF',
                       'SF',
                       'Contrast',
                       'Ori',
                       'PosX',
                       'PosY'
                       ]
    
    for stim_attribute in stim_attributes:
        stim_table[stim_attribute] = get_attribute_by_sweep(data, DG_idx, stim_attribute)[:len(stim_table)]
    
    return stim_table

def center_surround_table(data,twop_frames):
    
    center_idx = get_stimulus_index(data,'center')
    surround_idx = get_stimulus_index(data,'surround')
    
    timing_table = get_sweep_frames(data,center_idx)

    stim_table = init_table(twop_frames,timing_table)

    stim_table['TF'] = get_attribute_by_sweep(data,center_idx,'TF')[:len(stim_table)]
    stim_table['SF'] = get_attribute_by_sweep(data,center_idx,'SF')[:len(stim_table)]
    stim_table['Contrast'] = get_attribute_by_sweep(data,center_idx,'Contrast')[:len(stim_table)]
    stim_table['Center_Ori'] = get_attribute_by_sweep(data,center_idx,'Ori')[:len(stim_table)]
    stim_table['Surround_Ori'] = get_attribute_by_sweep(data,surround_idx,'Ori')[:len(stim_table)]

    return stim_table

def init_table(twop_frames,timing_table):
    return pd.DataFrame(np.column_stack((twop_frames[timing_table['start']],twop_frames[timing_table['end']])), columns=('Start', 'End'))

def get_stimulus_index(data, stim_name):
    """Return the index of stimulus in data.
    Returns the position of the first occurrence of stim_name in data. Raises a
    KeyError if a stimulus with a name containing stim_name is not found.
    Inputs:
        data (dict-like)
            -- Object in which to search for a named stimulus.
        stim_name (str)
    Returns:
        Index of stimulus stim_name in data.
    """
    for i_stim, stim_data in enumerate(data['stimuli']):
        if stim_name in stim_data['stim_path']:
            return i_stim

    raise KeyError('Stimulus with stim_name={} not found!'.format(stim_name))
    
def get_display_sequence(data, stimulus_idx):

    display_sequence = np.array(
        data['stimuli'][stimulus_idx]['display_sequence']
    )
    pre_blank_sec = int(data['pre_blank_sec'])
    display_sequence += pre_blank_sec
    display_sequence *= int(data['fps'])  # in stimulus frames

    return display_sequence
    
def get_sweep_frames(data, stimulus_idx, verbose = True):

    sweep_frames = data['stimuli'][stimulus_idx]['sweep_frames']
    timing_table = pd.DataFrame(
        np.array(sweep_frames).astype(np.int), columns=('start', 'end')
    )
    timing_table['dif'] = timing_table['end'] - timing_table['start']

    display_sequence = get_display_sequence(data, stimulus_idx)

    timing_table.start += display_sequence[0, 0]
    for seg in range(len(display_sequence) - 1):
        for index, row in timing_table.iterrows():
            if row.start >= display_sequence[seg, 1]:
                timing_table.start[index] = (
                    timing_table.start[index]
                    - display_sequence[seg, 1]
                    + display_sequence[seg + 1, 0]
                )
    timing_table.end = timing_table.start + timing_table.dif
    expected_sweeps = len(timing_table)
    timing_table = timing_table[timing_table.end <= display_sequence[-1, 1]]
    timing_table = timing_table[timing_table.start <= display_sequence[-1, 1]]
    actual_sweeps = len(timing_table)

    if verbose:
        print(data['stimuli'][stimulus_idx]['stim_path'])
        print('Found ' + str(actual_sweeps) + ' of ' + str(expected_sweeps) + ' expected sweeps.')

    return timing_table

def get_attribute_by_sweep(data, stimulus_idx, attribute):

    attribute_idx = get_attribute_idx(data, stimulus_idx, attribute)

    sweep_order = data['stimuli'][stimulus_idx]['sweep_order']
    sweep_table = data['stimuli'][stimulus_idx]['sweep_table']

    num_sweeps = len(sweep_order)

    attribute_by_sweep = np.zeros((num_sweeps,))
    attribute_by_sweep[:] = np.NaN

    unique_conditions = np.unique(sweep_order)
    for i_condition, condition in enumerate(unique_conditions):
        sweeps_with_condition = np.argwhere(sweep_order == condition)[:, 0]

        if condition > -1:  # blank sweep is -1
            if attribute.find('Size')!=-1:
                attribute_by_sweep[sweeps_with_condition] = sweep_table[condition][attribute_idx][0]
            else:
                attribute_by_sweep[sweeps_with_condition] = sweep_table[condition][attribute_idx]

    return attribute_by_sweep
    
def get_center_coordinates(data):
    
    center_idx = get_stimulus_index(data,'center')
    stim_definition = data['stimuli'][center_idx]['stim']
    
    position_idx = stim_definition.find('pos=array(')
    coor_start = position_idx + stim_definition[position_idx:].find('[') + 1
    coor_end = position_idx + stim_definition[position_idx:].find(']')
    comma_idx = position_idx + stim_definition[position_idx:].find(',')
    
    x_coor = float(stim_definition[coor_start:comma_idx])
    y_coor = float(stim_definition[(comma_idx+1):coor_end])
    
    return x_coor, y_coor
    
def get_attribute_idx(data, stimulus_idx, attribute):
    """Return the index of attribute in data for the given stimulus.
    Returns the position of the first occurrence of attribute. Raises a
    KeyError if not found.
    """
    attribute_names = data['stimuli'][stimulus_idx]['dimnames']
    for attribute_idx, attribute_str in enumerate(attribute_names):
        if attribute_str == attribute:
            return attribute_idx

    raise KeyError(
        'Attribute {} for stimulus_ids {} not found!'.format(
            attribute, stimulus_idx
        )
    )
    
def print_all_stim_attributes(data,stimulus_idx):

    for attribute_str in data['stimuli'][stimulus_idx]['dimnames']:
        print(attribute_str)
        
def print_all_stim_types(data):
    
    num_stim = len(data['stimuli'])
    for ns in range(num_stim):
        print(data['stimuli'][ns]['stim_path'])
    
def load_stim(exptpath, verbose=True):
    """Load stim.pkl file into a DataFrame.
    Inputs:
        exptpath (str)
            -- Directory in which to search for files with _stim.pkl suffix.
        verbose (bool)
            -- Print filename (if found).
    Returns:
        DataFrame with contents of stim pkl.
    """
    # Look for a file with the suffix '_stim.pkl'
    pklpath = None
    for f in os.listdir(exptpath):
        if f.endswith('_stim.pkl'):
            pklpath = os.path.join(exptpath, f)
            if verbose:
                print("Pkl file:", f)

    if pklpath is None:
        raise IOError(
            'No files with the suffix _stim.pkl were found in {}'.format(
                exptpath
            )
        )

    return pd.read_pickle(pklpath)
    
def load_sync(exptpath, verbose=True):

    # verify that sync file exists in exptpath
    syncpath = None
    for f in os.listdir(exptpath):
        if f.endswith('_sync.h5'):
            syncpath = os.path.join(exptpath, f)
            if verbose:
                print("Sync file:", f)
    if syncpath is None:
        raise IOError(
            'No files with the suffix _sync.h5 were found in {}'.format(
                exptpath
            )
        )    

    # load the sync data from .h5 and .pkl files
    d = Dataset(syncpath)
    if verbose:
        print(d.line_labels)
    vsync_2p_label = get_2p_vsync_line_label(d)
    vsync_stim_label = get_stim_vsync_line_label(d)
    photodiode_label = get_photodiode_line_label(d)

    # set the appropriate sample frequency
    sample_freq = d.meta_data['ni_daq']['counter_output_freq']

    # get sync timing for each channel
    twop_vsync_fall = d.get_falling_edges(vsync_2p_label) / sample_freq
    stim_vsync_fall = (
        d.get_falling_edges(vsync_stim_label)[1:] / sample_freq
    )  # eliminating the DAQ pulse
    photodiode_rise = d.get_rising_edges(photodiode_label) / sample_freq

    ptd_rise_diff = np.ediff1d(photodiode_rise)
    
    plt.figure()
    plt.plot(photodiode_rise,np.zeros((len(photodiode_rise),)),'o')
    #plt.xlim(0,100)
    plt.show()
    
    plt.figure()
    plt.hist(ptd_rise_diff,range=[0,5])
    plt.show()

    # make sure all of the sync data are available
    channels = {
        'twop_vsync_fall': twop_vsync_fall,
        'stim_vsync_fall': stim_vsync_fall,
        'photodiode_rise': photodiode_rise,
    }
    channel_test = []
    for chan in list(channels.keys()):
        # Check that signal is high at least once in each channel.
        channel_test.append(any(channels[chan]))
        if not any(channels[chan]):
            print(chan+' is empty!')
    if not all(channel_test):
        raise RuntimeError('Not all channels present. Sync test failed.')
    elif verbose:
        print("All channels present.")

    # print(photodiode_rise)
    
    print('Num 2P vsync_falls: '+str(len(twop_vsync_fall)))
    print('Num photodiode_rises: '+str(len(photodiode_rise)))
    print('Num stimulus vsync_falls: '+str(len(stim_vsync_fall)))
    
    # test and correct for photodiode transition errors
    ptd_rise_diff = np.ediff1d(photodiode_rise)
    short = np.where(np.logical_and(ptd_rise_diff > 0.1, ptd_rise_diff < 0.3))[
        0
    ]
    medium = np.where(np.logical_and(ptd_rise_diff > 0.5, ptd_rise_diff < 1.5))[
        0
    ]
    ptd_start = 3
    for i in medium:
        if set(range(i - 2, i)) <= set(short):
            ptd_start = i + 1
            
    if photodiode_rise.max() <= stim_vsync_fall.max():
        print('photodiode ends before stim_vsync already.')
        ptd_end = len(ptd_rise_diff)
    else:
        print('truncating photodiode to end before stim_vsync.')
        ptd_end = np.where(photodiode_rise > stim_vsync_fall.max())[0][0] - 1
    print('ptd_end: ' +str(ptd_end)+ ' max photodiode ' + str(photodiode_rise.max())+' max stim '+ str(stim_vsync_fall.max()))


    if ptd_start > 3 and verbose:
        print('ptd_start: ' + str(ptd_start))
        print("Photodiode events before stimulus start.  Deleted.")

    ptd_errors = []
    while any(ptd_rise_diff[ptd_start:ptd_end] < 1.8):
        error_frames = (
            np.where(ptd_rise_diff[ptd_start:ptd_end] < 1.8)[0] + ptd_start
        )
        print("Photodiode error detected. Number of frames:", len(error_frames))
        photodiode_rise = np.delete(photodiode_rise, error_frames[-1])
        ptd_errors.append(photodiode_rise[error_frames[-1]])
        ptd_end -= 1
        ptd_rise_diff = np.ediff1d(photodiode_rise)

    first_pulse = ptd_start
    stim_on_photodiode_idx = 60 + 120 * np.arange(0, ptd_end - ptd_start, 1)

    stim_on_photodiode = stim_vsync_fall[stim_on_photodiode_idx]
    photodiode_on = photodiode_rise[
        first_pulse + np.arange(0, ptd_end - ptd_start, 1)
    ]
    delay_rise = photodiode_on - stim_on_photodiode

    delay = np.mean(delay_rise[:-1])
    if verbose:
        print("monitor delay: ", delay)

    # adjust stimulus time to incorporate monitor delay
    stim_time = stim_vsync_fall + delay

    # convert stimulus frames into twop frames
    twop_frames = np.empty((len(stim_time), 1))
    for i in range(len(stim_time)):
        # crossings = np.nonzero(np.ediff1d(np.sign(twop_vsync_fall - stim_time[i]))>0)
        crossings = (
            np.searchsorted(twop_vsync_fall, stim_time[i], side='left') - 1
        )
        if crossings < (len(twop_vsync_fall) - 1):
            twop_frames[i] = crossings
        else:
            twop_frames[i : len(stim_time)] = np.NaN
            warnings.warn('Acquisition ends before stimulus.', RuntimeWarning)
            break

    return twop_frames, twop_vsync_fall, stim_vsync_fall, photodiode_rise

def get_2p_vsync_line_label(dataset_obj):
    
    for label in dataset_obj.line_labels:
        if label.find('2p')>-1 and label.find('vsync')>-1:
            return label
    warnings.warn('2p vsync line not found!', RuntimeWarning)
    sys.exit()
  
def get_stim_vsync_line_label(dataset_obj):
    
    for label in dataset_obj.line_labels:
        if label.find('stim')>-1 and label.find('vsync')>-1:
            return label      
    warnings.warn('stim vsync line not found!', RuntimeWarning)
    sys.exit()

def get_photodiode_line_label(dataset_obj):
    
    for label in dataset_obj.line_labels:
        if label.find('photodiode')>-1:
            return label
    warnings.warn('photodiode line not found!', RuntimeWarning)
    sys.exit()
  
if __name__=='__main__':  
    
    #exptpath = '/Users/danielm/Desktop/py_code/StimTable/sample_sessions/session_A/'
    #three_session_A_tables(exptpath)
    
    #exptpath = '/Users/danielm/Desktop/py_code/StimTable/sample_sessions/session_B/'
    #three_session_B_tables(exptpath)
    
    #exptpath = '/Users/danielm/Desktop/py_code/StimTable/sample_sessions/session_C/'
    #three_session_C_tables(exptpath)
    
     #exptpath = '/Users/danielm/Desktop/py_code/StimTable/sample_sessions/MovieClips/'
     #MovieClips_tables(exptpath,verbose=True)
    
     #exptpath = '/Users/danielm/Desktop/stim_sessions/SizeByContrast_day1to9/'
     #SizeByContrast_tables(exptpath)
     
     # exptpath = '/Users/danielm/Desktop/stim_sessions/Deepscope_test_3/'
     # omFish_gratings_tables(exptpath,verbose=True)
     
     # exptpath = '/Users/danielm/Desktop/stim_sessions/Deepscope_day1_1143565396/'
     # st = SizeByContrast_tables(exptpath)
     
     exptpath = '/Volumes/Extreme Pro/visual_behavior/'
     session_ID = 792619807
     st = VisualBehavior_NM1_table(exptpath,session_ID)
     print(st)
     
     #exptpath = '/Users/danielm/Desktop/stim_sessions/Deepscope_day0_test_2/'
     #SparseNoise_tables(exptpath)