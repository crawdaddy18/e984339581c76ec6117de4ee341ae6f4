import time
import sys
import av
import tellopy
import json
import threading
from confluent_kafka import Producer



flight_time = 30 # seconds
frames_per_second = 20.0



def get_cluster_name():
  with open('/opt/mapr/conf/mapr-clusters.conf', 'r') as f:
    first_line = f.readline()
    return first_line.split(' ')[0]

def create_stream(stream_path):
  if not os.path.islink(stream_path):
    os.system('maprcli stream create -path ' + stream_path + ' -produceperm p -consumeperm p -topicperm p -copyperm p -adminperm p')





def get_drone_video(drone):
    global frames_per_second
    cluster_name = get_cluster_name()
    stream_path = '/mapr/demo.mapr.com/video_stream'
    topic = "raw"
    producer = Producer({'streams.producer.default.stream': stream_path, 'message.max.bytes': 10000000})


    current_sec = 0
    last_frame_time = 0
    container = av.open(drone.get_video_stream())
    try:
        start_time = time.time()
        received_frames = 0
        sent_frames = 0

        while True:
            for frame in container.decode(video=0):
                received_frames += 1
                # producer.produce(topic, jpeg.tobytes())
                current_time = time.time()
                if current_time > (last_frame_time + float(1/frames_per_second)):
                    # print("producing frame {}".format(frame.index))
                    frame.to_image().save("/mapr/demo.mapr.com/images/frame-{}.jpg".format(frame.index))
                    producer.produce(topic, json.dumps({"index":frame.index}))
                    sent_frames += 1
                    last_frame_time = time.time()

                # Print stats every second
                elapsed_time = time.time() - start_time
                if int(elapsed_time) != current_sec:
                    sys.stdout.write("Elapsed : {} s, received {} fps , sent {} fps                 \r".format(elapsed_time,received_frames,sent_frames))
                    sys.stdout.flush()
                    received_frames = 0
                    sent_frames = 0
                    current_sec = int(elapsed_time)


    # Catch exceptions
    except Exception as ex:
        print(ex)



def main():
    
    drone = tellopy.Tello()
    drone.connect()
    drone.wait_for_connection(60)

    # create video thread
    videoThread = threading.Thread(target=get_drone_video,args=[drone])
    videoThread.start()

    input("Press Enter to exit...")

    exit(1)


if __name__ == '__main__':
    main()