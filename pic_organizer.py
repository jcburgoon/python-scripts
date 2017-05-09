#!/usr/bin/env python

import exifread, argparse, glob, os, datetime, shutil, hashlib

def move_picture(pic_path, pic_date, pic_dest, dup_dir):
    dest_dir = str(pic_dest) + str(pic_date.year) + "-" + str(pic_date.month) + "/"

    pic_md5 = get_file_md5(pic_path)

    # if the md5 for the picture is not in the list of md5s add it and move the picture to the destination folder based on the exif tag
    if pic_md5 not in md5_list:
        md5_list.append(pic_md5)

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

    # else move the duplicate picture to the duplicates directory
    else:
        shutil.move(pic_path, dup_dir + str(os.path.basename(pic_path)))

    return

def get_file_md5(file_name):
    filehash = hashlib.md5()

    with open(file_name, 'rb') as fh:
        buf = fh.read()
        filehash.update(buf)

    return filehash.hexdigest()

if __name__ == "__main__":
    # create md5_list needed for move_picture()
    global md5_list
    md5_list = []

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

    # create unknown & duplicates directories in the desitination if they do not exist
    if not os.path.exists(args.destination + "/unknown/"):
        os.makedirs(args.destination + "/unknown/")
    
    if not os.path.exists(args.destination + "/duplicates/"):
        os.makedirs(args.destination + "/duplicates/")

    for pic in sorted(picture_list):

        p = open(pic, "rb")

        # stop_tag will stop processing the file once the tag is found. should be a minor perf improvement
        tags = exifread.process_file(p, stop_tag="EXIF DateTimeOriginal")

        # attempt to move picture if it has the proper EXIF tag
        #if tags and tags["EXIF DateTimeOriginal"]:
        try:
            pic_datetime = datetime.datetime.strptime(str(tags["EXIF DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S")
            move_picture(pic, pic_datetime, args.destination, args.destination + "/duplicates/")
        except KeyError:
            print str(pic) + " does not have the EXIF tag!\n"
            shutil.move(pic, args.destination + "/unknown/")

        p.close()
        
    quit()
