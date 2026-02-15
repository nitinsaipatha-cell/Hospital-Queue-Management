import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field
import heapq
import time
import csv
import os
import random
import threading
from typing import List, Tuple

# -------------------------
# Desktop export path (confirmed)
# -------------------------
DESKTOP_PATH = "/Users/nitinsaimac/Desktop"

# -------------------------
# Data model
# -------------------------
@dataclass(order=False)
class Patient:
    id: int
    name: str
    age: int
    severity: int
    urgency: int
    booking_time: float
    appointment_type: str = "walk-in"
    notes: str = ""
    priority_tuple: Tuple = field(default=None, compare=False)

    def compute_priority(self) -> Tuple:
        age_priority = 1 if self.age < 12 or self.age >= 60 else 0
        appt_boost = 2 if self.appointment_type.lower() == "emergency" else (1 if self.appointment_type.lower() == "appointment" else 0)
        tup = (-(self.severity + appt_boost), -self.urgency, -age_priority, self.booking_time, self.id)
        self.priority_tuple = tup
        return tup

    def summary(self) -> str:
        bt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.booking_time))
        return f"[{self.id}] {self.name} | Age:{self.age} | Sev:{self.severity} | Urg:{self.urgency} | {self.appointment_type} | {bt}"

# -------------------------
# Real-time priority queue
# -------------------------
class HospitalQueue:
    def __init__(self):
        self._heap = []
        self._id_counter = 0
        self._lock = threading.Lock()

    def add_patient(self, name: str, age: int, severity: int, urgency: int,
                    appointment_type: str = "walk-in", notes: str = "", booking_time: float = None) -> Patient:
        if booking_time is None:
            booking_time = time.time()
        with self._lock:
            self._id_counter += 1
            p = Patient(self._id_counter, name, age, severity, urgency, booking_time, appointment_type, notes)
            heapq.heappush(self._heap, (p.compute_priority(), p))
            return p

    def pop_next(self) -> Patient:
        with self._lock:
            if not self._heap:
                return None
            return heapq.heappop(self._heap)[1]

    def peek_next(self) -> Patient:
        with self._lock:
            return self._heap[0][1] if self._heap else None

    def list_queue(self) -> List[Patient]:
        with self._lock:
            for _, p in self._heap:
                p.compute_priority()
            return [p for _, p in sorted(self._heap, key=lambda x: x[0])]

    def size(self) -> int:
        with self._lock:
            return len(self._heap)

    def clear(self):
        with self._lock:
            self._heap = []
            self._id_counter = 0

# -------------------------
# Export utility
# -------------------------
def export_patients_to_csv(patients: List[Patient], filename: str):
    filepath = os.path.join(DESKTOP_PATH, filename)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "age", "severity", "urgency", "appointment_type", "booking_time"])
        for p in patients:
            writer.writerow([p.id, p.name, p.age, p.severity, p.urgency, p.appointment_type,
                             time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.booking_time))])
    return filepath

# -------------------------
# Simulation logic
# -------------------------
def simulate_live_and_export(hq: HospitalQueue, how_many=30, doctors=2, arrival_interval=(1,4),
                             export_name="simulation_serviced.csv", progress_callback=None, seed=None):
    rng = random.Random(seed) if seed is not None else random.Random()
    now = time.time()
    for i in range(how_many):
        name = f"P{i+1}"
        age = rng.randint(1, 90)
        severity = rng.choices([1,2,3,4], weights=[40,30,20,10])[0]
        urgency = rng.randint(1, 10)
        appt = rng.choices(["walk-in", "appointment", "emergency"], weights=[60,30,10])[0]
        booking_time = now + i * rng.randint(*arrival_interval)
        hq.add_patient(name, age, severity, urgency, appt, "", booking_time=booking_time)
        if progress_callback:
            try: progress_callback(i+1, how_many)
            except Exception: pass

    serviced = []
    current_time = now
    while hq.size() > 0:
        for d in range(doctors):
            p = hq.pop_next()
            if p is None: break
            waiting_time = max(0, int(current_time - p.booking_time))
            serviced.append((p, waiting_time))
            current_time += rng.randint(3, 8)
            if progress_callback:
                try: progress_callback(len(serviced), how_many)
                except Exception: pass
        if len(serviced) >= how_many: break

    filepath = os.path.join(DESKTOP_PATH, export_name)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id","name","age","severity","urgency","appointment_type","booking_time","wait_seconds"])
        for p, w in serviced:
            writer.writerow([p.id, p.name, p.age, p.severity, p.urgency, p.appointment_type,
                             time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.booking_time)), w])
    return filepath, serviced

# -------------------------
# Tkinter GUI
# -------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Hospital Queue Optimization System")
        self.root.geometry("950x600")
        self.hq = HospitalQueue()
        self._create_widgets()
        self._populate_sample_patients()

    def _create_widgets(self):
        left = ttk.Frame(self.root, padding=10)
        left.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left, text="Add Patient", font=("Helvetica", 14, "bold")).pack(pady=(0,6))
        self.name_var = tk.StringVar()
        ttk.Label(left, text="Name").pack(anchor=tk.W); ttk.Entry(left, textvariable=self.name_var, width=25).pack()
        self.age_var = tk.IntVar(value=30)
        ttk.Label(left, text="Age").pack(anchor=tk.W); ttk.Entry(left, textvariable=self.age_var, width=10).pack()
        self.severity_var = tk.IntVar(value=2)
        ttk.Label(left, text="Severity (1-Mild .. 4-Critical)").pack(anchor=tk.W)
        ttk.Spinbox(left, from_=1, to=4, textvariable=self.severity_var, width=5).pack()
        self.urgency_var = tk.IntVar(value=5)
        ttk.Label(left, text="Urgency (1..10)").pack(anchor=tk.W)
        ttk.Spinbox(left, from_=1, to=10, textvariable=self.urgency_var, width=5).pack()
        self.appt_var = tk.StringVar(value="walk-in")
        ttk.Label(left, text="Appointment Type").pack(anchor=tk.W)
        ttk.Combobox(left, values=["walk-in","appointment","emergency"], textvariable=self.appt_var, state="readonly", width=18).pack()
        ttk.Label(left, text="Notes").pack(anchor=tk.W)
        self.notes_txt = tk.Text(left, height=4, width=25); self.notes_txt.pack()
        ttk.Button(left, text="Add Patient", command=self.add_patient).pack(pady=6, fill=tk.X)
        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        ttk.Button(left, text="Call Next Patient", command=self.call_next).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="Peek Next", command=self.peek_next).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="Export Queue Snapshot", command=self.export_snapshot).pack(fill=tk.X, pady=4)
        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        ttk.Label(left, text="Simulation", font=("Helvetica", 12, "bold")).pack(pady=(6,4))
        self.sim_n_var = tk.IntVar(value=30)
        self.sim_doc_var = tk.IntVar(value=2)
        ttk.Label(left, text="Arrivals").pack(anchor=tk.W); ttk.Entry(left, textvariable=self.sim_n_var, width=8).pack()
        ttk.Label(left, text="Doctors").pack(anchor=tk.W); ttk.Entry(left, textvariable=self.sim_doc_var, width=8).pack()
        self.sim_button = ttk.Button(left, text="Run Simulation (Background)", command=self.run_simulation_thread)
        self.sim_button.pack(pady=6, fill=tk.X)
        self.sim_progress = ttk.Label(left, text=""); self.sim_progress.pack()
        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        ttk.Button(left, text="Clear Queue", command=self.clear_queue).pack(fill=tk.X, pady=4)

        right = ttk.Frame(self.root, padding=10)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(right, text="Current Queue (by priority)", font=("Helvetica", 14, "bold")).pack(anchor=tk.W)
        self.queue_listbox = tk.Listbox(right, width=80, height=12); self.queue_listbox.pack(fill=tk.X, pady=6)
        bottom = ttk.Frame(right); bottom.pack(fill=tk.BOTH, expand=True, pady=(8,0))
        ttk.Button(bottom, text="Export Current Queue", command=self.export_snapshot).pack(side=tk.LEFT, padx=6)
        ttk.Button(bottom, text="Load Sample Patients", command=self._populate_sample_patients).pack(side=tk.LEFT, padx=6)
        ttk.Button(bottom, text="Show Queue Stats", command=self.show_stats).pack(side=tk.LEFT, padx=6)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)
        self._refresh_queue_view()

    def add_patient(self):
        name = self.name_var.get().strip()
        if not name: messagebox.showwarning("Input needed", "Please enter patient name."); return
        try: age = int(self.age_var.get()); severity = int(self.severity_var.get()); urgency = int(self.urgency_var.get())
        except Exception: messagebox.showwarning("Input error", "Age / severity / urgency must be integers."); return
        if not (0 <= age <= 130) or not (1 <= severity <= 4) or not (1 <= urgency <= 10):
            messagebox.showwarning("Input error", "Check age/severity/urgency ranges."); return
        appt = self.appt_var.get(); notes = self.notes_txt.get("1.0", tk.END).strip()
        p = self.hq.add_patient(name, age, severity, urgency, appt, notes)
        self.status_var.set(f"Added patient {p.summary()}"); self._refresh_queue_view()

    def call_next(self):
        p = self.hq.pop_next()
        if p is None: messagebox.showinfo("No patients", "Queue is empty."); return
        messagebox.showinfo("Calling Next", f"Call patient:\n{p.summary()}"); self.status_var.set(f"Called {p.name}"); self._refresh_queue_view()

    def peek_next(self):
        p = self.hq.peek_next()
        if p is None: messagebox.showinfo("No patients", "Queue is empty."); return
        messagebox.showinfo("Next Patient", p.summary())

    def export_snapshot(self):
        patients = self.hq.list_queue()
        if not patients: messagebox.showinfo("No data", "Queue is empty; nothing to export."); return
        filename = f"hospital_queue_snapshot_{int(time.time())}.csv"
        filepath = export_patients_to_csv(patients, filename)
        messagebox.showinfo("Exported", f"Saved queue snapshot to:\n{filepath}")

    def run_simulation_thread(self):
        try: n=int(self.sim_n_var.get()); docs=int(self.sim_doc_var.get())
        except Exception: messagebox.showwarning("Input error", "Simulation inputs must be integers."); return
        if n <= 0 or docs <= 0: messagebox.showwarning("Input error", "Arrivals and doctors must be positive."); return
        self.sim_button.config(state="disabled"); self.status_var.set("Scheduling simulation...")
        t = threading.Thread(target=self._run_simulation, args=(n, docs), daemon=True); t.start()

    def _run_simulation(self, n, docs):
        self.root.after(0, lambda: self.status_var.set("Simulation running..."))
        self.root.after(0, lambda: self.sim_progress.config(text="0/%d" % n))
        sim_hq = HospitalQueue()
        try:
            filepath, serviced = simulate_live_and_export(sim_hq, how_many=n, doctors=docs, progress_callback=self._sim_progress)
            self.root.after(0, lambda: self.status_var.set(f"Simulation complete: {len(serviced)} serviced."))
            self.root.after(0, lambda: self.sim_button.config(state="normal"))
            self.root.after(0, lambda: messagebox.showinfo("Simulation finished", f"Serviced {len(serviced)} patients.\nExport saved to:\n{filepath}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Simulation error", f"{e}"))
            self.root.after(0, lambda: self.sim_button.config(state="normal"))
            self.root.after(0, lambda: self.status_var.set("Simulation failed"))
        finally: self.root.after(0, lambda: self.sim_progress.config(text=""))

    def _sim_progress(self, done, total):
        try: self.root.after(0, lambda: self.sim_progress.config(text=f"{done}/{total}"))
        except Exception: pass

    def show_stats(self):
        size=self.hq.size(); peek=self.hq.peek_next()
        msg=f"Queue size: {size}\nNext patient: {peek.summary() if peek else 'None'}"
        messagebox.showinfo("Queue Stats", msg)

    def clear_queue(self):
        if messagebox.askyesno("Confirm", "Clear the whole queue?"):
            self.hq.clear(); self._refresh_queue_view(); self.status_var.set("Queue cleared")

    def _refresh_queue_view(self):
        self.queue_listbox.delete(0, tk.END)
        for p in self.hq.list_queue(): self.queue_listbox.insert(tk.END, p.summary())
        self.root.after(1500, self._refresh_queue_view)

    def _populate_sample_patients(self):
        samples=[("Rohit",65,2,6,"appointment"),("Sana",30,4,9,"emergency"),("Kavi",8,3,8,"walk-in"),
                 ("Maya",50,1,3,"walk-in"),("Arjun",72,2,5,"walk-in"),("Priya",25,4,10,"appointment")]
        self.hq.clear()
        for name, age, sev, urg, appt in samples: self.hq.add_patient(name, age, sev, urg, appt)
        self.status_var.set("Sample patients loaded")

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
