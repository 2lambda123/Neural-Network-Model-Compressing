'''
convert the *.caffemodel generated by DNS to compressed format.
'''

import sys
import os
import numpy as np
import pycaffe_header
import caffe

def outputLayerInfo(layername, nz_percentage):
    print "layer %s's nonzero percentage: %f"%(layername, nz_percentage)


compressed_model = "cmprd.model"

# TODO: 
help_ ='''
Usage:
    dns_model_compress.py <model.prototxt> <source.caffemodel> <target.cmodel>
    Set the CAFFE_ROOT in the source file.
'''
#######################################################

try:
    argv_list = list(sys.argv)
    prototxt_file = argv_list[1]
    caffemodel = argv_list[2]
except IndexError as e:
    print e
    sys.exit()

if not os.path.exists(caffemodel):
    print "Error: caffemodel does NOT exist!"
    sys.exit()
elif not os.path.exists(prototxt_file):
    print "Error: prototxt file does NOT exist!"
    sys.exit()
    
caffe.set_mode_cpu()

print "prototxt_file: %s "%(prototxt_file)
print "weights: %s"%(caffemodel)

net = caffe.Net(prototxt_file, caffe.TEST, weights=caffemodel)
#net = caffe.Net(prototxt_file, caffemodel, caffe.TEST)

f = open(compressed_model, 'wb')

# with open(compressed_model, 'wb') as f:
# num_total = 0
# num_total_nonzero = 0
# num_conv = np.zeros(2, dtype=np.int32)
num_nz_conv = np.zeros(2, dtype=np.int32)
# num_ip = np.zeros(2, dtype=np.int32)
num_nz_ip = np.zeros(2, dtype=np.int32)

for param_name in net.params.keys():
    if 'conv' in param_name and len(net.params[param_name]) > 2:
        conv_w = net.params[param_name][0].data.astype(np.float32).flatten()
        conv_b = net.params[param_name][1].data.astype(np.float32).flatten()
        mask_cw = net.params[param_name][2].data.astype(np.float32).flatten()
        mask_cb = net.params[param_name][3].data.astype(np.float32).flatten()
        print "shape of conv_w/conv_b/mask_cw/mask_cb: ", conv_w.shape, conv_b.shape, mask_cw.shape, mask_cb.shape
        
        nz_idx_w = np.nonzero(mask_cw)[0].astype(np.int32)
        nz_conv_w = conv_w[nz_idx_w].astype(np.float32)
        nz_idx_b = np.nonzero(mask_cb)[0].astype(np.int32)
        nz_conv_b = conv_b[nz_idx_b].astype(np.float32)

        num_nz_conv[0] = nz_conv_w.size
        num_nz_conv[1] = nz_conv_b.size
        print "type of nz_idx_w: %s"%(type(nz_idx_w))
        print "conv layer: \n  nz_w/w: %8d/ %8d\n  nz_b/b: %8d/ %8d"\
              %(num_nz_conv[0], conv_w.size, num_nz_conv[1], conv_b.size) 
        num_nz_conv.tofile(f)
        nz_conv_w.tofile(f)
        nz_idx_w.tofile(f)
        nz_conv_b.tofile(f)
        nz_idx_b.tofile(f)

    elif ('ip' in param_name or 'fc' in param_name):
        ip_w = net.params[param_name][0].data.astype(np.float32).flatten()
        ip_b = net.params[param_name][1].data.astype(np.float32).flatten()

        mask_ipw = net.params[param_name][2].data.astype(np.float32).flatten()
        mask_ipb = net.params[param_name][3].data.astype(np.float32).flatten()
        print "len of ip_w/ip_b/mask_ipw/mask_ipb: ", ip_w.size, ip_b.size, mask_ipw.size, mask_ipb.size
        print "shape of ip_w/ip_b/mask_ipw/mask_ipb: ", ip_w.shape, ip_b.shape, mask_ipw.shape, mask_ipb.shape

        nz_idx_w = np.nonzero(mask_ipw)[0].astype(np.int32)
        nz_ip_w = ip_w[nz_idx_w]
        nz_idx_b = np.nonzero(mask_ipb)[0].astype(np.int32)
        nz_ip_b = ip_b[nz_idx_b]

        num_nz_ip[0] = nz_ip_w.size
        num_nz_ip[1] = nz_ip_b.size

        print "ip layer: \n  nz_w/w: %8d/ %8d\n  nz_b/b: %8d/ %8d"\
              %(num_nz_ip[0], ip_w.size, num_nz_ip[1], ip_b.size)
        num_nz_ip.tofile(f)
        nz_ip_w.tofile(f)
        nz_idx_w.tofile(f)
        nz_ip_b.tofile(f)
        nz_idx_b.tofile(f)

    else:
        pass

f.close()

