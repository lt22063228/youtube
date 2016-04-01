'''
Created on Nov 13, 2015

@author: lin
'''
import db_session
import itertools
import os
import subprocess
import codecs

class DataManip:
    def block_dat(self, dir, train_file, test_file, sep):
        if not os.path.exists(dir + "/block/"):
            os.makedirs(dir + "/block/")

        # do train data
        file = open(train_file, "r")
        fixed_train = open(dir + "/block/fixed.train", "w")
        sampled_train = open(dir + "/block/sampled.train", "w")
        train_libfm = open(dir + "/block/train.libfm", "w")
    
        userIdx, videoIdx = 0, 0
        user_map, video_map = {}, {}
        for line in file:
            user, video = line.split(sep)[0], line.split(sep)[1]
            if user not in user_map:
                user_map[user] = userIdx
                userIdx += 1
            if video not in video_map:
                video_map[video] = videoIdx
                videoIdx += 1
            fixed_train.write(str(user_map[user]) + "\n")
            sampled_train.write(str(video_map[video]) + "\n")
            train_libfm.write("1\n")
            
        # do test data
        file = open(test_file, "r")
        fixed_test = open(dir + "/block/fixed.test", "w")
        sampled_test = open(dir + "/block/sampled.test", "w")
        test_libfm = open(dir + "/block/test.libfm", "w")
    
        for line in file:
            user, video = line.split(sep)[0], line.split(sep)[1]
            if user not in user_map:
                user_map[user] = userIdx
                userIdx += 1
            if video not in video_map:
                video_map[video] = videoIdx
                videoIdx += 1
            fixed_test.write(str(user_map[user]) + "\n")
            sampled_test.write(str(video_map[video]) + "\n")
            test_libfm.write("0\n")
    
        fixed_x = open(dir + "/block/fixed.x", "w")
        for i in range(userIdx):
            fixed_x.write(str(i) + ":" + "1\n")
    
        sampled_x = open(dir + "/block/sampled.x", "w")
        for i in range(videoIdx):
            sampled_x.write(str(i) + ":" + "1\n")
            
        # write the mapping
        u_mapfile = open(dir + "/block/user.map", "w")
        v_mapfile = open(dir + "/block/video.map", "w")
        for user in user_map:
            u_mapfile.write(str(user_map[user]) + sep + user + '\n')
        for video in video_map:
            v_mapfile.write(str(video_map[video]) + sep + video + '\n')

    def get_triple(self, dirpath, sparsity, sep, database): 
        import numpy as np
        import pandas as pd
        import math
        import codecs
        import MySQLdb as ms
        def make_dat_file(file, res):
            for idx in range(len(res)):
                delt = 0
                user, video, time = res[idx];
                file.write(user + sep + video + sep + time.strftime("%s") + "\n")
 
        db = ms.connect(host='localhost', port = 3306, user='root', passwd='123456', db = database, charset='utf8', use_unicode=True)
        cursor = db.cursor()
        query_train = 'select train.* from train'
        query_test = 'select test.* from test'
            
        print query_train
        print query_test

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
         
        cursor.execute(query_train)
        res = []
        for u,v,t in cursor:
            res.append((u,v,t))

        file = codecs.open(dirpath + "/train_" + sparsity + ".dat", "w", encoding='utf8')
        make_dat_file(file, res)
        file.close()        
         
        cursor.execute(query_test)
        res = []
        for u,v,t in cursor:
            res.append((u,v,t))

        file = codecs.open(dirpath + "/test_" + sparsity + ".dat", "w", encoding='utf8')
        make_dat_file(file, res)
        file.close() 

    

                
    def cal_prec(self, block_path):
        # load the mapping
        umapf = open(block_path + '/user.map', 'r')
        vmapf = open(block_path + '/video.map', 'r')
        umap, vmap = {}, {}
        
        for line in umapf:
            i, u = line.split(' ')[0], line.split(' ')[1]
            umap[i] = u
        for line in vmapf:
            i, v = line.split(' ')[0], line.split(' ')[1]
            vmap[i] = v
        
        
        fixed_test = file(block_path + "/fixed.test", "r")
        sampled_test = file(block_path + "/sampled.test", "r")
        fixed_x = file(block_path + "/fixed.x", "r")
        
        # recommend list
        rec_user_video = {}
        for line in fixed_x:
            user = line.split(":")[0]
            rec_user_video[user] = []
        print "len of user: ", len(rec_user_video)  
  
            
        rank_list_dir = block_path + "/output"
        for _, _, filenames in os.walk(rank_list_dir):
            for filename in filenames:
                filepath = rank_list_dir + "/" + filename
                uname = filename[:-4]
                rank_list = open(filepath, "r")
                for line in rank_list:
                    video = line.split('\t')[0]
                    rec_user_video[uname].append(video)
        
        # true list
        test_user_video = {}
        for user, video in itertools.izip(fixed_test, sampled_test):
            user, video = user[:-1], video[:-1]
            if user not in test_user_video:
                test_user_video[user] = [video]
            else:
                test_user_video[user].append(video)
        
        for K in range(1,21):

            sum_of_precision = 0.0
            sum_of_recall = 0.0
            sum_of_ave_precision = 0.0
            sum_of_users = 0.0
            user_list = []

            count = 0
            for user in rec_user_video:
                count += 1
                if user not in test_user_video: 
                    continue
                if len(rec_user_video[user]) == 0: 
                    continue

                test_video_len = len(test_user_video[user])              
                denominator = min(K, test_video_len)
                cul_denom = 0.0
                hit = 0.0
                ap = 0.0
                has_one = False

                for video in rec_user_video[user][:denominator]:
                    cul_denom += 1.0
                    if video in test_user_video[user]:
                        has_one = True
                        hit += 1.0
                        ap += hit/cul_denom * 1/denominator
                
                sum_of_recall += hit/test_video_len
                sum_of_precision += hit/denominator
                sum_of_ave_precision += ap
                sum_of_users += 1.0
                if has_one: user_list.append(umap[user][:-1])
            
            print "K: ", K
            print "count: ", count
            print "sum of users: ", sum_of_users
            print "precision: ", sum_of_precision / sum_of_users
            print "recall: ", sum_of_recall / sum_of_users
            print "map: ", sum_of_ave_precision / sum_of_users
            print "hit_user: ", user_list
                
    def avg_interval(self, path, sep):
        file = codecs.open(path, 'r', encoding = 'utf8')       
        avg = []
        cum = 0.
        cnt = 0
        preu = ''
        pret = 0
        for line in file:
            line = line.rstrip()
            u, v, t = line.split(sep)
            t = int(t)
            if u != preu:
                if cnt == 0: pass
                else: 
                    avg.append(cum/cnt)
                cum = 0.
                cnt = 0
                preu = u
                pret = t
                continue
            
            if t-pret <= 3600:
                cum += (t-pret)
                cnt += 1
                pret = t
        
#         print avg
        import matplotlib.pyplot as plt
        plt.hist(avg, bins=200)
        plt.show()
            
    def plot_convergence(self, path, sep):       
        import matplotlib.pyplot as plt
        # These are the colors that will be used in the plot
        color_sequence = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
                  '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
                  '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
                  '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']
        # plot to be 1.33x wider than tall
        fig, ax = plt.subplots(1,1,figsize=(40,9))
        # fig, ax = plt.subplots(1,3)
        
        # ensure that the axis ticks only show up on the bottom and left of the plot
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        
        # limit the range of the plot to only where the data is.
#         plt.xlim()
#         plt.ylim(0.,)
        
        # make sure axis ticks are large enough to be easily read.
        plt.xticks()
        plt.yticks()
        
#         dir = path + '/graph_data'
        dir = path + '/graph_data'
        
        

        fclus = []
        texts = []
        for item in os.listdir(dir):
            if os.path.isdir(os.path.join(dir,item)): continue
            fclus.append(open(os.path.join(dir,item),'r'))
            texts.append(item)
                
        xclu, yclu = [], []
        precs, recalls, mean_aps = [], [], []
        cnt = 0
        maxclu = []
        count = 0
        for i in range(len(fclus)):
            cnt = 0
            xclu.append([0])
            yclu.append([0.])
            precs.append([0.]); recalls.append([0.]); mean_aps.append([0.])

            maxclu.append(0.)
            for line in fclus[i]:
                cnt += 1
                if cnt == 1: continue
                if (cnt-1)%1 == 0: 
                    count += 1
                    line = line.rstrip()
#                     print line.split('\t')
                    iternum, loss, prec, recall, mean_ap, rank_grad, clu_grad, rankscore = line.split('\t')
#                     iternum, _, prec, recall, rank_grad, clu_grad, hit, rankscore = line.split('\t')


#                     iternum, _, prec, hit, rankscore = line.split('\t')

#                     iternum = int(iternum); hit = float(hit)
#                     xclu[i].append(iternum); yclu[i].append(hit)
#                     maxclu[i] = maxclu[i] if maxclu[i] > hit else hit

#                     iternum = int(iternum); loss = float(loss)
#                     xclu[i].append(iternum); yclu[i].append(loss)
#                     maxclu[i] = maxclu[i] if maxclu[i] > loss else loss

#                     iternum = int(iternum); rankscore = float(rankscore)
#                     xclu[i].append(iternum); yclu[i].append(rankscore)
#                     maxclu[i] = maxclu[i] if maxclu[i] > rankscore else rankscore

                    # iternum = int(iternum); prec = float(prec)
                    # xclu[i].append(iternum); yclu[i].append(prec)
                    # maxclu[i] = maxclu[i] if maxclu[i] > prec else prec

                    # iternum = int(iternum); recall = float(recall)
                    # xclu[i].append(iternum); yclu[i].append(recall)
                    # maxclu[i] = maxclu[i] if maxclu[i] > recall else recall

                    # iternum = int(iternum); mean_ap = float(mean_ap)
                    # xclu[i].append(iternum); yclu[i].append(mean_ap)
                    # maxclu[i] = maxclu[i] if maxclu[i] > mean_ap else mean_ap

#                     iternum = int(iternum); rank_grad = float(rank_grad)
#                     xclu[i].append(iternum); yclu[i].append(rank_grad)
#                     maxclu[i] = maxclu[i] if maxclu[i] > rank_grad else rank_grad

#                     iternum = int(iternum); clu_grad = float(clu_grad)
#                     xclu[i].append(iternum); yclu[i].append(clu_grad)
#                     maxclu[i] = maxclu[i] if maxclu[i] > clu_grad else clu_grad

                    prec = float(prec); precs[i].append(prec)

                    recall = float(recall); recalls[i].append(recall)

                    iternum = int(iternum); mean_ap = float(mean_ap)
                    xclu[i].append(iternum); mean_aps[i].append(mean_ap)
            
        cnt += 1
        count += 1
        print len(precs[0]), len(xclu[0])

        names = ['precision', 'recall', 'MAP']
        targets = [precs, recalls, mean_aps]
        for i in range(3):
            plt.subplot(131+i)
            plt.xlabel("number of iteration")
            plt.ylabel(names[i])
            for j in range(len(fclus)):
                # print len(xclu[j]), len(targets[i][j])
                line_clu = plt.plot(xclu[j], targets[i][j], lw=2.5, color = color_sequence[j], label = texts[j])
            plt.legend(loc='lower right')


#         plt.xlabel("number of iteration")
#         plt.ylabel("MAP")
#         for i in range(len(fclus)):
#             line_clu = plt.plot(xclu[i], yclu[i], lw=2.5, color = color_sequence[i], label = texts[i])
# #             plt.text(cnt, maxclu[i], texts[i], fontsize = 14, color = color_sequence[i+1])
#         plt.legend(loc = 'lower right')
# #         plt.legend(loc = 'upper left')
        plt.show()
            
    def cluster(self, dir, sep, table, order, database, spa):
        import numpy as np
        import pandas as pd
        import math
        import codecs
        import MySQLdb as ms

        db = ms.connect(host='localhost', port = 3306, user='root', passwd='123456', db = database, charset='utf8', use_unicode=True)
        cursor = db.cursor()
        if database == 'youtube':
            query = 'select '+table+'.* from '+table + ' order by '+order+'Id,published'
        elif database == 'new_vod':
            query = 'select '+table+'.* from '+table + ' order by '+order+',published'
        print query
        cursor.execute(query)
        
        umap = {}
        vmap = {}
        for u,v,t in cursor:
    
            if u not in umap: umap[u] = []
            umap[u].append((v,int(t.strftime("%s"))))
    
            if v not in vmap: vmap[v] = []
            vmap[v].append((u,int(t.strftime("%s"))))
            
        if order == 'user':
            window = 7200
            s = spa
            outfile = codecs.open(dir+'/cu'+table+ '_' + sparsity + '.dat','w',encoding='utf8')
            realmap = umap
        elif order == 'video':
            window = 7200
            outfile = codecs.open(dir+'/cv'+table+ '_' + sparsity + '.dat','w',encoding='utf8')
            realmap = vmap
    
        for key in realmap:
            values = realmap[key]
            for i in range(len(values)):
                value1, t1 = values[i]
                for j in range(i+1,len(values)):
                    value2, t2 = values[j]
                    delt = t2 - t1
                    if delt > window: break
                    outfile.write(key + sep + value1 + sep + value2 + sep + str(delt) + '\n')     
    
    def countDifferent(self, path):
        if path.endswith("pop.lst"):
            path = path[:path.rfind('/')]
            
            ui = {}; vi = {}
            file = open(path + "/block/user.map", 'r')
            for line in file:
                id, user = line.rstrip().split('\t')
                ui[user] = id
            file = open(path + '/block/video.map', 'r')
            for line in file:
                id, video = line.rstrip().split('\t')
                vi[video] = id
            

            
            file = open(path + "/train_80_20.dat", 'r')
            pred = {}; s = set()
            vmap = {}; done = {}
            for line in file:
                u, v, _ = line.rstrip().split('\t')
                u = ui[u]; v = vi[v]
                if u not in pred: pred[u] = []

                if u not in done: done[u] = []
                else: done[u].append(v)

                if v not in vmap: vmap[v] = 1
                else: vmap[v] = vmap[v] + 1

            countlist = vmap.items()
            countlist = sorted(countlist, key=lambda x: x[1], reverse = True)
            for user in done:
                cc = 0
                for v, _ in countlist:
                    if v not in done[user]:
                        pred[user].append(v)
                        cc += 1
                        s.add(v)
                    else: continue
                    if cc == 50: break
            
            return (s,pred)
            
        
        file = open(path, 'r')
        s = set()
        pred = {}
        for line in file:
            line = line.rstrip()
            lines = line.split('\t')
            user = lines[0][:-1]
            pred[user] = []
            for i in range(len(lines)):
                if i == 0: 
                    pred[lines[0][:-1]] = []
                    continue
                s.add(lines[i])
                pred[user].append(lines[i])
                

        print "different predction: " + str(len(s))
        return (s,pred)
        
    def getDone(self, path, pred_set, pred_dict, user_num):
          # uimap, iumap, vimap, ivmap
        file = path + "/block/user.map"
        uimap = {}; iumap = {}; vimap = {}; ivmap = {}
        done = {}
        for line in open(file,'r'):
            id, user = line.rstrip().split('\t')
            iumap[id] = user; uimap[user] = id
            done[id] = []
            
        file = path + "/block/video.map"
        for line in open(file,'r'):
            id, video = line.rstrip().split('\t')
            ivmap[id] = video; vimap[video] = id
           
        file = path + "/test_80_20.dat"
        for line in open(file,'r'):
            user, video, _ = line.rstrip().split('\t')
            user = uimap[user]; video = vimap[video]
            done[user].append(video)

        vcount = {}; tcount = {}
        file = path + "/train_80_20.dat"
        for line in open(file,'r'):
            user, video, _ = line.rstrip().split('\t')
            user = uimap[user]; video = vimap[video]
            if video not in vcount: vcount[video] = 1
            else: vcount[video] += 1
            if user not in tcount: tcount[user] = 0
            else: tcount[user] += 1
            
            
            
#         for user in done:
#             done[user] = done[user][0:50]

        # only for top 100 users
        done_number = []
        for user in done:
            done_number.append(tcount[user])
        done_number.sort(reverse = True)
        done_number = done_number[:user_num]
        
            
        s = set()
        tmp_done = {}
        for user in done:
            if len(done[user]) in done_number: 
                tmp_done[user] = done[user]
                for v in tmp_done[user]:
                    s.add(v)
                
        cnt = 0
        for user in tmp_done:
            for video in tmp_done[user]:
                if video in pred_dict[user]:
                    cnt += 1 
            

        return cnt, len(s) 
            


if __name__ == "__main__":
    dm = DataManip()
    dirpath = "/home/lin/workspace/data/youku"
    db = 'new_vod'
#     dirpath = "/home/lin/workspace/data/youtube"
#     db = 'youtube'
    block_path = dirpath + "/block"
    sparsity = "80_20"
    sep = "\t"
    train = dirpath + '/train_' + sparsity + '.dat'
    test = dirpath + '/test_' + sparsity + '.dat'

#     dm.get_triple(dirpath,sparsity = sparsity,sep = sep, database = db)
#     dm.cluster(dir = dirpath,sep = sep,table = 'train',order = 'user',database = db,spa = sparsity)
#     dm.cluster(dir = dirpath,sep = sep,table = 'test',order = 'user',database = db,spa = sparsity)
#     dm.cluster(dir = dirpath,sep = sep,table = 'train',order = 'video',database = db,spa = sparsity)
#     dm.cluster(dir = dirpath,sep = sep,table = 'test',order = 'video',database = db,spa = sparsity)
#     dm.block_dat(dirpath, train, test, sep)
#     dm.plot_convergence(dirpath,sep)


    dirpath = dirpath + '/cache'

    ################################################## fix the user number , vary the cache number
#     user_num = [100,500,1000]
#     cache_num = 30
#     bar_width = 0.2
#     cache_each = 10.
#     pred_set, pred_dict = dm.countDifferent(dirpath+"/clu_user.lst")
#      
#     xx = []; yy = []
#     for index in range(3):
#         x = []; y = []
#         for num in range(1,cache_num+1):
#             tmp_dict = {}
#             for user in pred_dict:
#                 tmp_dict[user] = pred_dict[user][0:num]
#             cnt, broad_num = dm.getDone(dirpath, pred_set, tmp_dict, user_num[index])
#             x.append(num); y.append((cnt-broad_num)/(cache_each*user_num[index]))
#         xx.append(x); yy.append(y)


    ################################################### fix the cache, vary the user number
#     bar_width = 0.2 * 20
#     cache_num = [5,15,25]
#     user_num = 1000
#     cache_each = 10.
#     pred_set, pred_dict = dm.countDifferent(dirpath+"/clu_user.lst")
#     xx = []; yy = []
#     for index in range(3):
#         x = []; y = []
#         for num in range(80, user_num+1, 20):
#             tmp_dict = {}
#             for user in pred_dict:
#                 tmp_dict[user] = pred_dict[user][0:cache_num[index]]
#             cnt, broad_num = dm.getDone(dirpath, pred_set, tmp_dict, num)
#             x.append(num); y.append((cnt-broad_num)/(cache_each*num))
#         xx.append(x); yy.append(y)
        
    ################################################## vary the rec method for user

    bar_width = 0.2 * 20
    user_num = 1000
    cache_num = 25
    cache_each = 10.
    paths = ["clu_user.lst", "sgd.lst", "pop.lst"]
    xx = []; yy = []
    for index in range(3):
        pred_set, pred_dict = dm.countDifferent(dirpath + '/' + paths[index])
        x = []; y = []
        for num in range(40, user_num+1, 20): ####### user num
            tmp_dict = {}
            for user in pred_dict:
                tmp_dict[user] = pred_dict[user][0:cache_num]
            cnt, broad_num = dm.getDone(dirpath, pred_set, tmp_dict, num)
            x.append(num); y.append((cnt-broad_num)/(cache_each*num))
        xx.append(x); yy.append(y)
    
    #################################################### start plot
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1,1,figsize=(40,9))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    plt.xlabel("user number")
    plt.ylabel("communication save(%)")
#     ax = plt.subplot(111)
    colors = ['r','g','b']
    bars = []
    offset = [-bar_width, 0, bar_width]
    for index in range(3):
        xxx = [(x+offset[index]) for x in xx[index]]
        if index == 1:
            plt.xticks(xxx[::2], xxx[::2])
        yyy = [each for each in yy[index]]
        bar_each = ax.bar(xxx, yyy, width = bar_width, color = [colors[index]])
        bars.append(bar_each)
#     ax.legend((bars[0], bars[1], bars[2]), ("user number: " + str(user_num[0]),"user number: " +  str(user_num[1]),"user number: " +  str(user_num[2])))
#     ax.legend((bars[0], bars[1], bars[2]), ("cache number: " + str(cache_num[0]),"cache number: " +  str(cache_num[1]),"cache number: " +  str(cache_num[2])))
    ax.legend((bars[0], bars[1], bars[2]), ("cluster based", "rank only", "pop based"))
#     line_clu = plt.bar(x, y, lw=2.5, color = '#1f77b4', label = "curve")
    plt.show()






































