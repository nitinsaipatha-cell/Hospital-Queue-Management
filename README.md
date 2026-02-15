# Smart Hospital Queue Optimization System

This repository contains a real-time hospital patient queue management system implemented using a priority-based scheduling algorithm. The system provides a graphical interface to register patients, compute treatment priority, and manage servicing efficiently.

The application evaluates severity, urgency, age group, appointment type, and arrival time to determine which patient should be treated next.

## Project Overview

This project simulates how hospitals can optimize patient flow using intelligent prioritization.

Patients are added through the GUI.  
The system continuously reorders the queue using a heap-based priority model.  
Doctors or receptionists can call or preview the next patient, export records, or run large-scale simulations.

The system is thread-safe and supports background processing.

## System Details

**Core Logic:** Priority Queue (heap)  
**Framework:** Tkinter (GUI)  
**Language:** Python  

### Priority Factors
- Severity level  
- Urgency  
- Children (<12) and seniors (60+)  
- Appointment type:
  - walk-in  
  - appointment  
  - emergency  
- Arrival / booking time  

## Repository Structure

|-- main.py  # Application with GUI and queue logic

|-- README.md  # Project documentation

*(Replace `main.py` with your file name if different.)*

## Requirements

Python 3.9+

No external packages are required.  
Only Python standard library modules are used.

## How to Run

Run the application using:

python main.py

**What the Program Does**

- Register new patients  
- Automatically compute their priority  
- Display the live queue  
- Call or peek the next patient  
- Run simulations with virtual arrivals  
- Export queue data to CSV  
- Show queue statistics  

**Export Information**

CSV files are automatically saved to:
/Users/nitinsaimac/Desktop

Exports may include:

- Current queue snapshots  
- Simulation results  
- Waiting time reports  

## Simulation Mode

The simulator can:

- Generate many virtual patients  
- Assign random severity & urgency  
- Simulate multiple doctors  
- Measure service order and waiting times  
- Export the results  

This is useful for performance testing and demonstrations.

## Applications

- Hospital reception systems  
- Emergency triage support  
- Queue optimization research  
- Academic demonstrations  
- Operations management studies

## Disclaimer

This project is developed for educational and academic purposes only.  
It is a simulation and should not replace professional medical triage systems.

## Author

**Nitin Sai Patha**
