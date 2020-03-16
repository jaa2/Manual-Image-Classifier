import queue
from PIL import Image
from multiprocessing import Process, Queue
from . import imageops

""" Maximum number of images in the cache """
CACHE_MAX_CAPACITY = 50

""" Class for controlling the loading of images """
class ImageLoader:
    
    """ Local image cache of OpenCV images """
    img_cache = {}
    
    """ Set of images currently being processed """
    cache_filenames_pending = set()
    
    """ Current target cache filter; image filenames not in this cache may be
        deleted. """
    cache_filter = []
    
    """ Create an ImageLoader
        @param view_dims    Dimensions of the letterbox images will be
            constrained to; a tuple (width, height).
        @param num_processes    Number of processes (image loading workers) to
            open """
    def __init__(self, view_dims, cache_max_size, num_processes = 8):
        self.view_dims = view_dims
        self.num_processes = num_processes
        self.cache_max_size = cache_max_size
        
        # Create queues and worker processes
        self.task_queue = Queue()
        self.done_queue = Queue()
        
        for i in range(num_processes):
            process = Process(target=self.__worker_run,
                              args=(self.task_queue, self.done_queue, i))
            process.start()
    
    """ Gets an image. If the image is not already in the image cache, the
        image will be loaded into the image cache. Note that images are
        distinguished by their filenames.
        @param filename Filename of the image to load.
        @param identifier   Image identifier for printing when the image is
            loaded
        @return Loaded OpenCV image """
    def get_image(self, filename, identifier = None):
        if filename not in self.img_cache:
            self.__image_add_to_queue(filename)
            self.__image_wait(filename)
            return self.img_cache[filename]
        else:
            return self.img_cache[filename]
    
    """ Update the cache. Images not in filename_list may be removed, and those
        that are but have not been loaded yet will be loaded in a different
        process.
        @param filename_list    Target list of image filenames to store in the
            image cache """
    def update_cache(self, filename_list):
        # Update the cache filter
        self.cache_filter = filename_list.copy()
        
        # Add new filenames to the queue
        for filename in filename_list:
            self.__image_add_to_queue(filename)
        
        # Get a newly loaded image from the queue
        # TODO: Make a max_new variable for maximum number of new images to add at once
        while True:
            try:
                self.__image_next_from_done()
            except queue.Empty:
                break
    
    """ This function must be called before the object is destroyed!
        It cleans up all child processes and waits for them to finish. """
    def clean_up(self):
        for i in range(self.num_processes):
            self.task_queue.put(None)
        # Process and remove all images from the done queue
        while len(self.cache_filenames_pending) > 0:
            try:
                self.__image_next_from_done()
            except queue.Empty:
                pass
    
    """ Update the dimensions of the image.
        @param view_dims (width, height) of new images """
    def set_view_dims(self, view_dims):
        self.view_dims = view_dims
    
    """ Retrieves the next image from the done queue.
        Note that a queue.Empty exception will be thrown if the done queue is
        empty.
        @return Loaded image filename """
    def __image_next_from_done(self):
        filename, img = self.done_queue.get(False)
        self.__image_add_to_cache(filename, img)
        self.cache_filenames_pending.discard(filename)
        return filename
    
    """ Waits for the image to be loaded into the cache, adding it to the queue
        if necessary. """
    def __image_wait(self, filename):
        self.__image_add_to_queue(filename)
        while True:
            try:
                loaded_filename = self.__image_next_from_done()
                if loaded_filename == filename:
                    break
            except queue.Empty:
                pass
        
    """ Adds an image filename to the queue if it is not already in the cache
        or queue. """
    def __image_add_to_queue(self, filename):
        if (filename not in self.img_cache
            and filename not in self.cache_filenames_pending):
            self.task_queue.put(filename)
            self.cache_filenames_pending.add(filename)
    
    """ Load an image from the disk and letterbox it to view_dims.
        @return OpenCV image """
    def __image_load(self, filename):
        new_image = Image.open(filename)
        new_image_resized = imageops.image_resize_to_fit(new_image,
                                                     self.view_dims[0],
                                                     self.view_dims[1])
        del new_image
        return new_image_resized
    
    """ Adds an image to the cache, freeing an older image if necessary. """
    def __image_add_to_cache(self, filename, image):
        if (filename not in self.img_cache
            and len(self.img_cache) >= self.cache_max_size):
            # Remove an old image; note that using "list" here allows us to
            # iterate over the dictionary keys AND modify them.
            for cache_filename in list(self.img_cache.keys()):
                if cache_filename not in self.cache_filter:
                    print("Removing " + cache_filename)
                    del self.img_cache[cache_filename]
                    break
        
        self.img_cache[filename] = image
    
    """ Main loop of a worker process.
        @param task_queue   Queue of image filenames to load
        @param done_queue   Queue of loaded images
        @param worker_id    ID of this worker """
    def __worker_run(self, task_queue, done_queue, worker_id):
        for filename in iter(task_queue.get, None):
            img = self.__image_load(filename)
            done_queue.put((filename, img))
            print("Worker " + str(worker_id) + " loaded " + filename)
        print("Worker " + str(worker_id) + " ended.")
