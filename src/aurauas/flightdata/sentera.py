# load sentera csv format

import fileinput
import math
import numpy as np
import os
import re

import navpy

d2r = math.pi / 180.0
g = 9.81

# empty class we'll fill in with data members
class Record: pass

def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    
def load(flight_dir):
    result = {}
    
    gps_data = []
    filter_data = []

    # load imu/gps data files
    imu_file = flight_dir + "/imu.csv"
    gps_file = flight_dir + "/gps.csv"
    filter_post = flight_dir + "/filter-post-ins.txt"
    
    # calibration by plotting and eye-balling (just finding center point, no
    # normalization cooked into calibration.)
    #hx_coeffs = np.array([ 1.0,  -1.5], dtype=np.float64)
    #hy_coeffs = np.array([ 1.0, -78.5], dtype=np.float64)
    #hz_coeffs = np.array([ 1.0, -156.5], dtype=np.float64)
    
    #~/Projects/PILLS/Phantom\ 3\ Flight\ Data/2016-03-22\ --\ imagery_0012\ -\ 400\ ft\ survey
    #hx_coeffs = np.array([ 0.01857771, -0.18006661], dtype=np.float64)
    #hy_coeffs = np.array([ 0.01856938, -1.20854406], dtype=np.float64)
    #hz_coeffs = np.array([ 0.01559645,  2.81011976], dtype=np.float64)

    # ~/Projects/PILLS/Phantom\ 3\ Flight\ Data/imagery_0009 - 0012
    #hx_coeffs = np.array([ 0.01789447,  3.70605872], dtype=np.float64)
    #hy_coeffs = np.array([ 0.017071,    0.7125617], dtype=np.float64)
    #hz_coeffs = np.array([ 0.01447557, -6.54621951], dtype=np.float64)
    
    # ~/Projects/PILLS/2016-04-04\ --\ imagery_0002
    # ~/Projects/PILLS/2016-04-14\ --\ imagery_0003
    # ~/Projects/PILLS/2016-04-14\ --\ imagery_0004
    #hx_coeffs = np.array([ 0.01658555, -0.07790598], dtype=np.float64)
    #hy_coeffs = np.array([ 0.01880532, -1.26548151], dtype=np.float64)
    #hz_coeffs = np.array([ 0.01339084,  2.61905809], dtype=np.float64)

    # ~/Projects/PILLS/2016-05-12\ --\ imagery_0004
    #hx_coeffs = np.array([ 0.01925678,  0.01527908], dtype=np.float64)
    #hy_coeffs = np.array([ 0.01890112, -1.18040666], dtype=np.float64)
    #hz_coeffs = np.array([ 0.01645011,  2.87769626], dtype=np.float64)

    #hx_func = np.poly1d(hx_coeffs)
    #hy_func = np.poly1d(hy_coeffs)
    #hz_func = np.poly1d(hz_coeffs)

    # ~/Projects/PILLS/2016-06-29\ --\ calibration_0002/
    # mag_affine = np.array(
    #     [[ 0.0223062041, -0.0002700799, -0.0001325525,  1.2016235718],
    #      [-0.0002700799,  0.0229484854,  0.0000356172,  0.1177744077],
    #      [-0.0001325525,  0.0000356172,  0.0206129279, -3.2713740483],
    #      [ 0.          ,  0.          ,  0.          ,  1.          ]]
    # )

    # Phantom 3 - Aug 2016 (ellipse cal)
    # mag_affine = np.array(
    #     [[ 0.0189725067,  0.0000203615,  0.0002139272, -0.0134053645],
    #      [ 0.0000760692,  0.0180178765,  0.0000389461, -1.044762755 ],
    #      [ 0.0002417847,  0.0000458039,  0.0171450614,  2.647911793 ],
    #      [ 0.          ,  0.          ,  0.          ,  1.          ]]
    # )
    # Phantom 3 - Aug 2016 (ekf cal)
    # mag_affine = np.array(
    #     [[ 0.0181297161,  0.000774339,  -0.002037224 , -0.2576406372],
    #      [ 0.0002434548,  0.018469032,   0.0016475328, -0.8452362072],
    #      [ 0.0000145964,  0.000267444,   0.0159433791,  2.5630653789],
    #      [ 0.          ,  0.         ,   0.          ,  1.          ]]
    # )

    # 2017-06-07_23-43-50
    mag_affine = np.array(
        [[ 0.0182094965,  0.0001891445,  0.0005079058, -1.0275778093],
         [ 0.0001891445,  0.0188836673,  0.0003014306, -0.7472003813],
         [ 0.0005079058,  0.0003014306,  0.0176589615,  0.9988130618],
         [ 0.          ,  0.          ,  0.          ,  1.          ]]
    )
    print(mag_affine)

    result['imu'] = []
    fimu = fileinput.input(imu_file)
    for line in fimu:
        #print line
        if not re.search('Time', line):
            tokens = line.split(',')
            #print len(tokens)
            if len(tokens) == 11 and isFloat(tokens[10]):
                #print '"' + tokens[10] + '"'
                (time, p, q, r, ax, ay, az, hx, hy, hz, temp) = tokens
                # remap axis before applying mag calibration
                p = -float(p)
                q =  float(q)
                r = -float(r)
                ax = -float(ax)*g
                ay =  float(ay)*g
                az = -float(az)*g
                hx = -float(hx)
                hy =  float(hy)
                hz = -float(hz)
                mag_orientation = 'random1'
                if mag_orientation == 'older':
                    #hx_new = hx_func(float(hx))
                    #hy_new = hy_func(float(hy))
                    #hz_new = hz_func(float(hz))
                    s = [hx, hy, hz]
                elif mag_orientation == 'newer':
                    # remap for 2016-05-12 (0004) data set
                    #hx_new = hx_func(float(-hy))
                    #hy_new = hy_func(float(-hx))
                    #hz_new = hz_func(float(-hz))
                    s = [-hy, -hx, -hz]
                elif mag_orientation == 'random1':
                    # remap for 2016-05-12 (0004) data set
                    #hx_new = hx_func(float(-hy))
                    #hy_new = hy_func(float(-hx))
                    #hz_new = hz_func(float(-hz))
                    s = [-hy, -hx, hz]
                # mag calibration mapping via mag_affine matrix
                hs = np.hstack( [s, 1.0] )
                hf = np.dot(mag_affine, hs)
                #print hf[:3]
                #norm = np.linalg.norm([hx_new, hy_new, hz_new])
                #hx_new /= norm
                #hy_new /= norm
                #hz_new /= norm
                
                imu = Record()
                imu.time = float(time)/1000000.0
                imu.p = p
                imu.q = q
                imu.r = r
                imu.ax = ax
                imu.ay = ay
                imu.az = az
                do_mag_transform = True
                if do_mag_transform:
                    imu.hx = hf[0]
                    imu.hy = hf[1]
                    imu.hz = hf[2]
                else:
                    imu.hx = s[0]
                    imu.hy = s[1]
                    imu.hz = s[2]
                #float(hf[0]), float(hf[1]), float(hf[2]),
                imu.temp = float(temp)
                result['imu'].append( imu )

    result['gps'] = []
    fgps = fileinput.input(gps_file)
    for line in fgps:
        if not re.search('Timestamp', line):
            # print line
            tokens = line.split(',')
            # print 'gps tokens:', len(tokens)
            if len(tokens) == 14:
                (time, itow, ecefx, ecefy, ecefz, ecefvx, ecefvy, ecefvz,
                 fixtype, posacc, spdacc, posdop, numsvs, flags) = tokens
            elif len(tokens) == 19:
                (time, itow, lat, lon, alt, ecefx, ecefy, ecefz,
                 ecefvx, ecefvy, ecefvz,
                 fixtype, posacc, spdacc, posdop, numsvs, flags,
                 diff_status, carrier_status) = tokens
                
            # wgs84 position
            pos_source = 'llh'  # 'llh' or 'ecef'
            llh = navpy.ecef2lla([float(ecefx)/100.0,
                                  float(ecefy)/100.0,
                                  float(ecefz)/100.0], "deg")
            # velocity
            ned = navpy.ecef2ned([float(ecefvx)/100.0,
                                  float(ecefvy)/100.0,
                                  float(ecefvz)/100.0],
                                 llh[0], llh[1], llh[2])
            if int(numsvs) >= 4:
                gps = Record()
                gps.time = float(time)/1000000.0
                #gps.status = int(status)
                gps.unix_sec = float(time)/1000000.0 # make filter happy
                gps.lat = float(lat)
                gps.lon = float(lon)
                gps.alt = float(alt)
                gps.vn = ned[0]
                gps.ve = ned[1]
                gps.vd = ned[2]
                result['gps'].append(gps)

    result['filter'] = []
    # load filter (post process) records if they exist (for comparison
    # purposes)
    if os.path.exists(filter_post):
        print('found filter-post-ins.txt, using that for ekf results')
        result['filter'] = []
        ffilter = fileinput.input(filter_post)
        for line in ffilter:
            tokens = re.split('[,\s]+', line.rstrip())
            lat = float(tokens[1])
            lon = float(tokens[2])
            if abs(lat) > 0.0001 and abs(lon) > 0.0001:
                filterpt = Record()
                filterpt.time = float(tokens[0])
                filterpt.lat = lat*d2r
                filterpt.lon = lon*d2r
                filterpt.alt = float(tokens[3])
                filterpt.vn = float(tokens[4])
                filterpt.ve = float(tokens[5])
                filterpt.vd = float(tokens[6])
                filterpt.phi = float(tokens[7])*d2r
                filterpt.the = float(tokens[8])*d2r
                psi = float(tokens[9])
                if psi > 180.0:
                    psi = psi - 360.0
                if psi < -180.0:
                    psi = psi + 360.0
                filterpt.psi = psi*d2r
                result['filter'].append(filterpt)

    return result

def save_filter_result(filename, data_store):
    f = open(filename, 'w')
    size = len(data_store.time)
    for i in range(size):
        line = "%.3f,%.10f,%.10f,%.2f,%.4f,%.4f,%.4f,%.2f,%.2f,%.2f,0" % \
               (data_store.time[i],
                data_store.lat[i]*180.0/math.pi,
                data_store.lon[i]*180.0/math.pi,
                data_store.alt[i], data_store.vn[i],
                data_store.ve[i], data_store.vd[i],
                data_store.phi[i]*180.0/math.pi,
                data_store.the[i]*180.0/math.pi,
                data_store.psi[i]*180.0/math.pi)
        f.write(line + '\n')
    f.close()

def rewrite_image_metadata_txt(base_dir, data_store):
    meta_file = os.path.join(base_dir, 'image-metadata.txt')
    new_file = os.path.join(base_dir, 'image-metadata-ekf.txt')

    if not os.path.isfile(meta_file):
        return
    
    f_out = open(new_file, 'w')
    f_out.write('File Name,Lat (decimal degrees),Lon (decimal degrees),Alt (meters MSL),Yaw (decimal degrees),Pitch (decimal degrees),Roll (decimal degrees),GPS Time (us since epoch)\n')

    i = 0
    for line in fileinput.input(meta_file):
        if fileinput.isfirstline():
            continue
        tokens = line.split(',')
        image = tokens[0]
        (lat, lon, alt, psi, the, phi, time_orig) = map(float, tokens[1:])
        time_sec = time_orig / 1000000.0       # convert seconds
        while data_store.time[i] < time_sec:
            i += 1
        line = "%s,%.8f,%.8f,%.4f,%.4f,%.4f,%.4f,%.0f" % \
               (image,
                data_store.nav_lat[i]*180.0/math.pi,
                data_store.nav_lon[i]*180.0/math.pi,
                data_store.nav_alt[i],
                data_store.psi[i]*180.0/math.pi,
                data_store.the[i]*180.0/math.pi,
                data_store.phi[i]*180.0/math.pi,
                time_orig)
        f_out.write(line + '\n');
    f_out.close()

def rewrite_pix4d_csv(base_dir, data_store):
    meta_file = os.path.join(base_dir, 'image-metadata.txt')
    pix4d_file = os.path.join(base_dir, 'pix4d-ekf.csv')

    if not os.path.isfile(meta_file):
        return
    
    f_out = open(pix4d_file, 'w')
    f_out.write('File Name,Lat (decimal degrees),Lon (decimal degrees),Alt (meters MSL),Roll (decimal degrees),Pitch (decimal degrees),Yaw (decimal degrees)\n')

    i = 0
    for line in fileinput.input(meta_file):
        if fileinput.isfirstline():
            continue
        tokens = line.split(',')
        image = tokens[0]
        (lat, lon, alt, psi, the, phi, time) = map(float, tokens[1:8])
        time /= 1000000.0       # convert seconds
        while data_store.time[i] < time:
            print(i, data_store.time[i], '<', time)
            i += 1
        line = "%s,%.8f,%.8f,%.4f,%.4f,%.4f,%.4f" % \
               (image,
                data_store.nav_lat[i]*180.0/math.pi,
                data_store.nav_lon[i]*180.0/math.pi,
                data_store.nav_alt[i],
                data_store.phi[i]*180.0/math.pi,
                data_store.the[i]*180.0/math.pi,
                data_store.psi[i]*180.0/math.pi)
        f_out.write(line + '\n');
    f_out.close()
