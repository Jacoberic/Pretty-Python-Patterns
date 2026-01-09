from time import time
import json
import os
import csv

class Timer():
    def __init__(self, timeout, segment_by_timeout=False):
        self.start_time = time()
        if segment_by_timeout:
            self.start_time = self.start_time // timeout * timeout - timeout
        self.timeout = timeout
        self.on = True

    @property
    def current_time(self):
        return time() - self.start_time
    
    @property
    def running(self):
        if self.on:
            return self.current_time < self.timeout
        else:
            return False

    @property
    def finished(self):
        if self.on:
            return self.current_time >= self.timeout
        else:
            return False#the timer hasn't finished if it's off

    @property
    def off(self):
        return not self.on

    @off.setter
    def off(self, value: bool):
        self.on = not value

    def reset(self):
        self.start_time = time()
        self.on = True

    def next(self):
        t = time()
        while self.start_time + self.timeout < t:
            self.start_time += self.timeout

class Spinner:
    def __init__(self):
        self.symbols = ["|", "/", "-", "\\"]
        self.index = 0
        self.timer = Timer(0.2)

    def spin(self):
        if self.timer.finished:
            self.timer.reset()
            print("\r" + self.symbols[self.index], end="")  # Carriage return to overwrite, display symbol
            self.index = (self.index + 1) % len(self.symbols)  # Cycle through the symbols

    def gui_spin(self):
        if self.timer.finished:
            self.timer.reset()
            symbol = self.symbols[self.index]  # Carriage return to overwrite, display symbol
            self.index = (self.index + 1) % len(self.symbols)  # Cycle through the symbols

            return symbol


def csv_to_matrix(file_name):
    with open(file_name, 'r') as file:
        data = [row for row in csv.reader(file)]

    return data

def matrix_to_csv(data, file_name):
    with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

class RollingList:
    def __init__(self, initial_list=None, length=100) -> None:
        """A rolling list that always contains the most recent "length" components.
        Used generally for keeping track of recent values for redundant fault checking, or for graphing.

        Args:
            initial_list (list, optional): Defaults to [].
            length (int, optional): Always is this length or less. Defaults to 100.
        """
        self._list = [] if initial_list is None else initial_list
        self.length = length

    def __str__(self) -> str:
        return str(self._list)

    def append(self, element):
        """Call List.append then removes the oldest element if it's over the self.length

        Args:
            element (_type_): The list element to add
        """
        self._list.append(element)
        if len(self._list) > self.length:
            self._list.pop(0)

    def all_less_than(self, value) -> bool:
        """Returns True if all values are less than value

        Args:
            value (any): value to compare to

        Returns:
            bool: all(element < value for element in self._list)
        """
        if len(self._list) < self.length:
            return None
        else:
            return all(element < value for element in self._list)

    def all_greater_than(self, value) -> bool:
        """Returns True if all values are greater than value

        Args:
            value (any): value to compare to

        Returns:
            bool: all(element > value for element in self._list)
        """
        if len(self._list) < self.length:
            return None
        else:
            return all(element > value for element in self._list)

    def all_non_empty(self) -> bool:
        """Returns True if all elements in the list have a length greater than 0

        Returns:
            bool: all(len(element) > 0 for element in self._list)
        """
        if len(self._list) < self.length:
            return None
        else:
            return all(len(element) > 0 for element in self._list)

    def all_true(self) -> bool:
        """returns True if all elements are True

        Returns:
            bool: all(self._list)
        """
        if len(self._list) < self.length:
            return None
        else:
            return all(self._list)

    def all_false(self) -> bool:
        """return False if all elements are False

        Returns:
            bool: any(self._list)
        """
        if len(self._list) < self.length:
            return None
        else:
            return not any(self._list)

    def majority(self):
        """Returns the element that occurs most frequently

        Returns:
            any: the element that occurs most frequently
        """
        if len(self._list) < self.length:
            return None
        else:
            unique_elements = list(set(self._list))
            majority_list = [(self._list.count(element), element) for element in unique_elements]
            majority_list.sort()
            majority = majority_list[-1][1]
            return majority

class _Settings:
    def __init__(self) -> None:
        #*Make a dictionary of all the settings names. These will be the keys and default values of the json dictionary
        self._class_dict = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):#We don't want system or private variables
                self._class_dict[key] = value
        
        #*Either a new settings file is generated or the keys from the file must match the defined keys
        try:
            with open(self._path, 'r') as file:
                json_dict = json.load(file)
        except Exception:#I believe an exception here means the file doesn't exist or is empty
            try:
                os.mkdir(os.path.dirname(self._path))#so try to make it
            except FileExistsError:#this failing I think means it's empty
                pass
            with open(self._path, 'w') as file:#regardless, write the class dictionary to the json
                json.dump(self._class_dict, file, indent=4)
        else:#check that the keys still match after loading
            rewrite = False
            for key in self._class_dict:
                if key in json_dict:#if the key is already in settings
                    self._class_dict[key] = json_dict[key]#load that value
                else:#otherwise
                    json_dict[key] = self._class_dict[key]#add the default value
                    rewrite = True#mark that the json needs rewriting

            remove_list = []
            for key in json_dict:
                if key not in self._class_dict:#mark old keys to be removed
                    remove_list.append(key)
                    rewrite = True

            for key in remove_list:#now actually remove them while outside a loop with the dictionary
                json_dict.pop(key)

            assert self._class_dict == json_dict#they should be fully synced now

            if rewrite:#rewrite the actual json if necessary
                with open(self._path, 'w') as file:#regardless, write the class dictionary to the json
                    json.dump(self._class_dict, file, indent=4)

            for key in self._class_dict:#now sync the _class_dict and the class dictinary (the actual values associated with the instance name i.e. settings.x)
                self.__dict__[key] = self._class_dict[key]

    def __setattr__(self, _k: str, _v) -> None:
        #*Change the value in the instance of the object
        super().__setattr__(_k, _v)

        #*If it's been initialized and it's not _path or _settings_dict set the json
        if self._initialized and not _k.startswith('_'):
            if self._readonly:
                raise Exception('Trying to assign to a readonly setting.')
            if _k not in self._class_dict:
                raise KeyError('Invalid key. Key not in original settings.')
            else:
                with open(self._path, 'r') as file:#pull up the dictionary
                    json_dict = json.load(file)
                json_dict[_k] = _v#change the appropriate entry
                with open(self._path, 'w') as file:#put it back
                    json.dump(json_dict, file, indent=4)

    def __str__(self) -> str:
        with open(self._path, 'r') as file:
            _settings = json.load(file)
        return _settings.__str__()

class Settings(_Settings):
    def __init__(self, readonly=False):
        #*This is where the json will be stored
        self._initialized = False
        self._path = 'settings/settings.json'
        self._readonly = readonly

        #*These are the default values for json dictionary entries. It won't let anymore be set besides these, and they'll show up in linting.
        self.username = ''
        self.password = ''

        super().__init__()
        self._initialized = True
