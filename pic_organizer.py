#!/usr/bin/env python

import exifread, argparse, glob, os, datetime, shutil

def move_picture(pic_path, pic_date, pic_dest):
    dest_dir = str(pic_dest) + str(pic_date.year) + "-" + str(pic_date.month) + "/"
    #create directory if it does not exist, then move the file (there can't be a dup name!)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        shutil.move(pic_path, dest_dir + str(os.path.basename(pic_path)))

    else:
        # check if the file exists
        if not os.path.isfile(dest_dir + str(os.path.basename(pic_path))):
             shutil.move(pic_path, dest_dir + str(os.path.basename(pic_path)))
        else:
             # if file exists, move with a new name -> -<# ms> appended to end of file name
             new_file_name = dest_dir + str(os.path.basename(pic_path)).split(".")[0] + "-" + str(datetime.datetime.now().microsecond) + ".jpg"
             # keep generating new file names until it doesnt exist
             while os.path.isfile(new_file_name):
                 new_file_name = dest_dir + str(os.path.basename(pic_path)).split(".")[0] + "-" + str(datetime.datetime.now().microsecond) + ".jpg"

             shutil.move(pic_path, new_file_name)

    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize pictures by date")
    parser.add_argument("-l", "--location", type=str, required=True, help="Picture location including trailing /")
    parser.add_argument("-d", "--destination", type=str, required=True, help="Place to move pictures including trailing /")
    args = parser.parse_args() # args.location, args.destination

    picture_list = glob.glob(args.location + "*.jpg")
    picture_list.extend(glob.glob(args.location + "*.JPG"))
    picture_list.extend(glob.glob(args.location + "*.jpeg"))
    picture_list.extend(glob.glob(args.location + "*.JPEG"))

    if not picture_list:
        print "No pictures found!"
        quit()

    # create unknown directory in the desitination if it does not exist
    if not os.path.exists(args.destination + "/unknown/"):
        os.makedirs(args.destination + "/unknown/")

    for pic in sorted(picture_list):

        p = open(pic, "rb")

        # stop_tag will stop processing the file once the tag is found. should be a minor perf improvement
        tags = exifread.process_file(p, stop_tag="EXIF DateTimeOriginal")

        # attempt to move picture if it has the proper EXIF tag
        try:
            pic_datetime = datetime.datetime.strptime(str(tags["EXIF DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S")
            move_picture(pic, pic_datetime, args.destination)
        except KeyError:
            print str(pic) + " does not have the EXIF tag!\n"
            shutil.move(pic, args.destination + "/unknown/")

        p.close()
        
    quit()
