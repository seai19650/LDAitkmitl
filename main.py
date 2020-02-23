import sys
sys.path.append("..") # Adds higher directory to python modules path.

from Util import Util
from LDAModeling import LDAModeling

import os
# This package is for downloading pdf
import urllib.request




"""
    1) download all files from a list of URLs and save to local (API server)
    require:
        local_path = "/Users/Kim/Documents/TestDownloadFiles/"
"""
# todo change these three variables
# define a local root to save files

# input_local_root = '/Users/Kim/Documents/trf_dir/TestDownloadFiles/'
input_local_root = '/Users/dhanamon/LDAitkmitl/TestDownloadFiles/'

# define an output directory to save an 'original' pyLDAvis html file
# output_dir = '/Users/Kim/Documents/trf_dir/PyLDAVizOutput/'
output_dir = '/Users/dhanamon/LDAitkmitl/PyLDAVizOutput/'
# define an output directory to save an 'original' pyLDAvis html file
pyLDAvis_output_file = 'docx_LDAvis_newmm_2n_postag_title_7n.html'

# define an output directory to save an 'thai' pyLDAvis html file
# th_output_dir = '/Users/Kim/Documents/trf_dir/PyLDAVizOutput/th/'
th_output_dir = '/Users/dhanamon/LDAitkmitl/PyLDAVizOutput/th/'
# define an output directory to save an 'thai' pyLDAvis html file
th_pyLDAvis_output_file = 'th_docx_LDAvis_newmm_2n_postag_title_7n.html'

urls = ['https://elibrary.trf.or.th/fullP/SRI61X0602/SRI61X0602_full.pdf',
        'https://elibrary.trf.or.th/fullP/RDG6240001/RDG6240001_full.pdf',
        'https://elibrary.trf.or.th/fullP/RDG6210003/RDG6210003_full.pdf',
        # 'https://elibrary.trf.or.th/fullP/RDG6140033/RDG6140033_full.pdf',
        # 'https://elibrary.trf.or.th/fullP/RDG6140024/RDG6140024_full.pdf',
        # 'https://elibrary.trf.or.th/fullP/RDG6140012/RDG6140012_full.pdf',
        # 'https://elibrary.trf.or.th/fullP/RDG6140022/RDG6140022_full.pdf',
        # 'https://elibrary.trf.or.th/fullP/RDG6140023/RDG6140023_full.pdf',
        # 'https://elibrary.trf.or.th/fullP/RDG60H0018/RDG60H0018_full.pdf',
        # 'https://elibrary.trf.or.th/fullP/RDG6140010/RDG6140010_full.pdf'
        ]

titles = ['การศึกษาวิเคราะห์การทุจริตคอร์รัปชันของขบวนการเครือข่ายนายหน้าข้ามชาติในอุตสาหกรรมประมงต่อเนื่องของประเทศไทย',
            'นวัตกรรมเพื่อพัฒนาท้องถิ่นตามแนวทางปรัชญาของเศรษฐกิจพอเพียง: กรณีศึกษาองค์กรปกครองส่วนท้องถิ่นในจังหวัดนครสวรรค์และอุทัยธานี',
            'การศึกษาผลประโยชน์ทางธุรกิจที่เกิดจากการนำเศษพลอยมาใช้ประโยชน์ในเชิงพาณิชย์มากขึ้น',
            # 'การศึกษาประสบการณ์การเรียนรู้ของเยาวชนกลุ่มชาติพันธุ์ในการสร้างความรู้ด้านนิเวศวัฒนธรรม ',
            # 'การวิจัยและพัฒนากระบวนการผลิตและพัฒนาครูโดยบูรณาการแนวคิดจิตตปัญญาศึกษา ระบบพี่เลี้ยง และการวิจัยเป็นฐานของคณะครุศาสตร์ มหาวิทยาลัยราชภัฏ ปีที่ 2',
            # 'การพัฒนาชุดการเรียนรู้วิชาศิลปะในชั้นเรียนแบบเรียนรวมที่มีนักเรียนตาบอดระดับมัธยมศึกษาตอนปลายและการทดลองขยายผล',
            # 'การวิจัยและพัฒนากระบวนการผลิตและพัฒนาครูโดยบูรณาการแนวคิดจิตปัญญาศึกษา การเป็นพี่เลี้ยงและการวิจัยเป็นฐาน ภาคกลาง-ภาคตะวันตก  ปีที่ 2 ',
            # 'ระบบและกระบวนการผลิตและพัฒนาครูโดยใช้โครงงานฐานวิจัย ในพื้นที่ภาคใต้ ปีที่ 2',
            # 'การศึกษาประวัติศาสตร์สังคมพหุวัฒนธรรมจากตำนานประวัติศาสตร์ท้องถิ่นภาคใต้',
            # 'โครงการวิจัยและพัฒนาแนวทางการหนุนเสริมทางวิชาการเพื่อพัฒนากระบวนการผลิตและพัฒนาครูโดยบูรณาการแนวคิดจิตตปัญญาศึกษา ระบบพี่เลี้ยง และการวิจัยเป็นฐานของคณะครุศาสตร์ มหาวิทยาลัยราชภัฏ'
            ]


print('========== Beginning file download with urllib2. ==========')
to_process_files = []
abs_file_paths = []
counter = 0
print(len(urls), len(titles))
for url in urls:
    file_ = Util.path_leaf(url)
    # print(file_)
    abs_file_path =  input_local_root + file_
    # print(abs_file_path)

    if not os.path.isfile(abs_file_path):
        try:
            print('downloading file from this url: \"{0}\" with this file name : \"{1}\".'.format(url, file_))
            urllib.request.urlretrieve(url, abs_file_path)
        except:
            print('An exception occurred when downloading a file from this url, \"{0}\"'.format(url))
            # Delete the title of a file that cannot be downloaded at a specific index.
            # This is to keep two lists of abs_file_paths and titles consistent.

            del titles[counter]

    else:
        print('-- This file, \"{0}\", already exists in: \"{1}\"! Therefore, this file will not be downloaded. --'.format(file_, input_local_root))
    to_process_files.append(file_)
    counter += 1

ldamodeling = LDAModeling()
ldamodeling.perform_topic_modeling(input_local_root, to_process_files, titles,
                                   output_dir, pyLDAvis_output_file, th_output_dir, th_pyLDAvis_output_file, max_no_topics = 7)


