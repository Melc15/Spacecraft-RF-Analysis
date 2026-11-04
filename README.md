# Spacecraft-RF-Analysis
# Spacecraft RF Link Analysis and Verification

## Overview

Python project for analyzing spacecraft radio-frequency (RF) communications using Voyager 1 and 2 communications.

The project estimates RF link performance over interplanetary distances, evaluates telemetry scenarios, applies an illustrative link acceptance criterion, runs automated tests, and generates a PDF verification report.

## Project Objectives

- Calculate transmitter equivalent isotropically radiated power (EIRP).
- Estimate free-space path loss over large distances.
- Model received signal power and ground-station noise characteristics.
- Calculate carrier-to-noise density ratio (C/N0) and energy per bit to noise density ratio (Eb/N0).
- Apply an illustrative acceptance criterion to telemetry scenarios.
- Verify software behaviour using automated unit tests.
- Maintain a requirements traceability matrix.
- Generate a PDF report containing simulated results and automated software test outcomes.

## Project Structure

| File or directory | Purpose |
|---|---|
| `spacecraft_config.py` | Defines the educational S-band and X-band RF configurations. |
| `link_budget.py` | Implements EIRP, free-space path loss, and link-budget calculations. |
| `run_link_budget.py` | Runs link-budget scenarios for estimated spacecraft distances. |
| `ground_station.py` | Models reference ground-station gain, noise temperature, G/T, and C/N0. |
| `telemetry_analysis.py` | Compares calculated Eb/N0 across telemetry data rates. |
| `verification.py` | Applies the illustrative link acceptance criterion. |
| `test_verification.py` | Contains seven automated tests for the verification logic. |
| `Tests/test_rf_test_system.py` | Contains nine tests for the separate RF amplifier test simulator. |
| `requirements_traceability.csv` | Maps verification requirements to their associated tests. |
| `generate_verification_report.py` | Runs pytest and generates the PDF verification report. |
| `results/voyager_verification_report.pdf` | Generated verification report. |

## Engineering Calculations

### Equivalent isotropically radiated power

EIRP combines transmitter power and transmitting antenna gain:

`EIRP (dBW) = Transmitter Power (dBW) + Antenna Gain (dBi)`

### Free-space path loss

The model estimates the attenuation of a radio signal travelling through free space:

`FSPL (dB) = 20 log10(4πd/λ)`

where `d` is the propagation distance in metres and `λ` is the signal wavelength in metres.

### Received power

The simplified link budget calculates received power from EIRP, free-space path loss, receiving antenna gain, and specified system losses:

`Pr (dBm) = EIRP (dBm) − FSPL (dB) + Gr (dBi) − L (dB)`

where `Gr` is receiving antenna gain and `L` represents the modelled system losses.

### Carrier-to-noise density ratio

The project estimates C/N0 using received carrier power and the receiver noise spectral density.

### Energy per bit to noise density ratio

The telemetry analysis uses:

`Eb/N0 (dB) = C/N0 (dB-Hz) − 10 log10(Rb)`

where `Rb` is the telemetry data rate in bits per second.

For a fixed C/N0, increasing the data rate decreases the calculated Eb/N0. Actual demodulation performance also depends on modulation, coding, receiver implementation, and operating conditions.

## Verification Approach

The project includes automated tests for:

- Expected Eb/N0 calculations.
- The relationship between data rate and Eb/N0.
- Positive, negative, and zero link-margin boundary conditions.
- Rejection of zero and negative data rates.
- Existing RF amplifier simulator behaviour, including fault detection and invalid inputs.

The requirements traceability CSV connects each of the seven Voyager verification requirements to a test function and expected result.

The PDF generator records the outcome of the complete pytest run, including its summary and process exit code.

## How to Run

Run commands from the project root directory.

### 1. Run the link-budget analysis

```bash
python run_link_budget.py
```

### 2. Run the ground-station analysis

```bash
python ground_station.py
```

### 3. Run telemetry analysis

```bash
python telemetry_analysis.py
```

### 4. Run the educational verification scenarios

```bash
python verification.py
```

### 5. Run the automated test suite

```bash
python -m pytest -v
```

### 6. Generate the verification report

```bash
python generate_verification_report.py
```

The generated report is saved to:

`results/voyager_verification_report.pdf`

The project requires Python, pytest, and ReportLab, along with the standard Python libraries used by the scripts. Install any missing dependencies in your chosen Python environment.

## Illustrative Results

The current educational model uses a C/N0 of 31.01 dB-Hz and an illustrative minimum Eb/N0 criterion of 3.00 dB.

| Scenario | Data rate | Calculated Eb/N0 | Model result |
|---|---:|---:|---|
| Normal real-time telemetry | 160 bps | 8.97 dB | PASS |
| High-rate playback | 1,400 bps | −0.45 dB | FAIL |
| Historical high-rate capability | 7,200 bps | −7.56 dB | FAIL |

These outcomes reflect the simplified model and selected criterion. They do not establish whether Voyager could or could not operate at any particular rate under actual mission conditions. The 7,200 bps scenario is labelled as historical capability, not current operation.

## Assumptions and Limitations

- Calculations use estimated spacecraft distances and configured RF parameters.
- The ground-station model uses reference assumptions rather than a complete, current operational DSN configuration.
- Some system losses are set to zero in the simplified link-budget scenarios.
- C/N0 is a model input or calculated estimate, not a live measurement.
- The minimum Eb/N0 threshold is illustrative and is not an official NASA requirement.
- The verification outcomes are not a substitute for link qualification, measured RF performance, or mission-specific engineering analysis.
- Passing software tests confirms the tested code behaviour; it does not independently validate the physical accuracy of the model.
- Traceability statuses are maintained in the CSV and should be reviewed against actual test execution when interpreting the report.

## Technologies

- Python
- pytest
- ReportLab
- CSV-based requirements traceability
- RF link-budget calculations
- Automated software verification and PDF reporting

## Engineering Skills Demonstrated

- RF communications analysis
- Satellite communications fundamentals
- Python programming and modular software design
- Unit testing and boundary-value testing
- Requirements traceability
- Automated test reporting
- Technical documentation
- Engineering assumptions, limitations, and verification discipline
