# 给安总做的图标可视化

# -*- coding: UTF-8 -*-
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import random

np.random.seed(1)

#这里导入你自己的数据
#......
#......
#x_axix，train_pn_dis这些都是长度相同的list()

#开始画图
# sub_axix = filter(lambda x:x%200 == 0, x_axix)
# plt.title('Result Analysis')

x = range(512)
y = np.random.rand(512)
plt.plot(x, y, color='skyblue', label='hammerhead shark')
# plt.plot(sub_axix, test_acys, color='red', label='testing accuracy')
# plt.plot(x_axix, train_pn_dis,  color='skyblue', label='PN distance')
# plt.plot(x_axix, thresholds, color='blue', label='threshold')
plt.legend() # 显示图例

plt.xlabel('Channel Index')
plt.ylabel('Activation')
plt.ylim((-1,2))
plt.show()