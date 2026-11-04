
"""
Automated RF Test and Verification System

"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)

#Configuration parameters for the RF test system

START_FREQUENCY_GHZ = 1.0
STOP_FREQUENCY_GHZ = 3.0
NUMBER_OF_POINTS = 101

MINIMUM_ACCEPTABLE_GAIN_DB = 18.0

FAULT_START_GHZ = 1.78
FAULT_FULL_START_GHZ = 1.85
FAULT_FULL_END_GHZ = 2.15
FAULT_END_GHZ = 2.22
FAULT_DROP_DB = 5.0

MEASUREMENT_NOISE_STD_DB = 0.08
RANDOM_SEED = 42

OUTPUT_FOLDER = Path("results")

#Simulated RF measurement and verification functions


def smoothstep(x):
    #Smooth transition between zero and one.
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def simulate_rf_measurement(frequencies_ghz, inject_fault=False):
    #Generate simulated amplifier gain measurements.

    frequencies_ghz = np.asarray(frequencies_ghz, dtype=float)

    if frequencies_ghz.ndim != 1 or frequencies_ghz.size == 0:
        raise ValueError("Frequencies must be a non-empty 1D array.")

    if not np.all(np.isfinite(frequencies_ghz)):
        raise ValueError("Frequencies must be finite.")

    rng = np.random.default_rng(RANDOM_SEED)

    nominal_gain_db = (
        22.0 - 1.5 * (frequencies_ghz - 2.0) ** 2
    )

    noise_db = rng.normal(
        loc=0.0,
        scale=MEASUREMENT_NOISE_STD_DB,
        size=frequencies_ghz.size,
    )

    measured_gain_db = nominal_gain_db + noise_db

    if inject_fault:
        ramp_in = smoothstep(
            (frequencies_ghz - FAULT_START_GHZ)
            / (FAULT_FULL_START_GHZ - FAULT_START_GHZ)
        )

        ramp_out = 1.0 - smoothstep(
            (frequencies_ghz - FAULT_FULL_END_GHZ)
            / (FAULT_END_GHZ - FAULT_FULL_END_GHZ)
        )

        fault_severity = np.minimum(ramp_in, ramp_out)
        measured_gain_db -= FAULT_DROP_DB * fault_severity

    return measured_gain_db


#Verification and evaluation functions


def evaluate_measurements(frequencies_ghz, gain_measurements_db):
    #Evaluate measurements against the minimum gain requirement.

    frequencies_ghz = np.asarray(frequencies_ghz, dtype=float)
    gain_measurements_db = np.asarray(
        gain_measurements_db, dtype=float
    )

    if frequencies_ghz.ndim != 1 or gain_measurements_db.ndim != 1:
        raise ValueError("Inputs must be one-dimensional arrays.")

    if frequencies_ghz.size == 0:
        raise ValueError("At least one measurement is required.")

    if frequencies_ghz.size != gain_measurements_db.size:
        raise ValueError("Frequency and gain arrays must have equal length.")

    if not np.all(np.isfinite(frequencies_ghz)):
        raise ValueError("Frequencies must be finite.")

    if not np.all(np.isfinite(gain_measurements_db)):
        raise ValueError("Gain measurements must be finite.")

    results = []

    for frequency, gain in zip(
        frequencies_ghz, gain_measurements_db
    ):
        margin_db = gain - MINIMUM_ACCEPTABLE_GAIN_DB

        results.append({
            "frequency_ghz": float(frequency),
            "measured_gain_db": float(gain),
            "minimum_gain_db": MINIMUM_ACCEPTABLE_GAIN_DB,
            "margin_db": float(margin_db),
            "result": (
                "PASS"
                if gain >= MINIMUM_ACCEPTABLE_GAIN_DB
                else "FAIL"
            ),
        })

    return results


def run_rf_test(inject_fault=False):
    #Execute the complete frequency sweep.

    frequencies_ghz = np.linspace(
        START_FREQUENCY_GHZ,
        STOP_FREQUENCY_GHZ,
        NUMBER_OF_POINTS,
    )

    gains_db = simulate_rf_measurement(
        frequencies_ghz,
        inject_fault=inject_fault,
    )

    return evaluate_measurements(frequencies_ghz, gains_db)


def summarize_results(results):
    #Calculate overall verification statistics.

    if not results:
        raise ValueError("Cannot summarize empty results.")

    gains = np.array([
        item["measured_gain_db"] for item in results
    ])

    passed = sum(item["result"] == "PASS" for item in results)
    failed = len(results) - passed

    minimum_gain = float(np.min(gains))
    worst_margin = minimum_gain - MINIMUM_ACCEPTABLE_GAIN_DB

    return {
        "total_tests": len(results),
        "passed": passed,
        "failed": failed,
        "minimum_measured_gain_db": minimum_gain,
        "worst_margin_db": worst_margin,
        "overall_result": "PASS" if failed == 0 else "FAIL",
    }

#Export functions for CSV, plot, and PDF report


def export_results(results):
    #Export detailed measurement results to CSV.

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_FOLDER / "rf_test_results.csv"

    fields = [
        "frequency_ghz",
        "measured_gain_db",
        "minimum_gain_db",
        "margin_db",
        "result",
    ]

    with output_file.open(
        "w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    return output_file

# Plotting function for gain vs frequency

def plot_results(results, inject_fault=False):
    #Plot gain, acceptance threshold, and failed measurements.

    frequencies = np.array([
        item["frequency_ghz"] for item in results
    ])
    gains = np.array([
        item["measured_gain_db"] for item in results
    ])
    passed = np.array([
        item["result"] == "PASS" for item in results
    ])
    failed = ~passed

    fig, ax = plt.subplots(figsize=(11, 6.5))

    ax.plot(
        frequencies,
        gains,
        linewidth=1.8,
        label="Simulated measured gain",
    )

    ax.axhline(
        MINIMUM_ACCEPTABLE_GAIN_DB,
        linestyle="--",
        linewidth=1.8,
        label=f"Minimum requirement ({MINIMUM_ACCEPTABLE_GAIN_DB:.1f} dB)",
    )

    if np.any(passed):
        ax.scatter(
            frequencies[passed],
            gains[passed],
            s=25,
            label="PASS",
            zorder=3,
        )

    if np.any(failed):
        ax.scatter(
            frequencies[failed],
            gains[failed],
            marker="x",
            s=42,
            label="FAIL",
            zorder=4,
        )

    mode = "Fault Injected" if inject_fault else "Normal Operation"
    ax.set_title(f"Automated RF Amplifier Verification — {mode}")
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Gain (dB)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    plot_file = OUTPUT_FOLDER / "rf_test_plot.png"

    fig.savefig(plot_file, dpi=180, bbox_inches="tight")
    plt.show()
    plt.close(fig)

    return plot_file


# PDF report generation function using ReportLab

def generate_pdf_report(results, summary, plot_file, inject_fault=False):
    #Generate a PDF report documenting the RF verification run.

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    pdf_file = OUTPUT_FOLDER / "rf_engineering_test_report.pdf"
    timestamp = datetime.now().astimezone().strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )

    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=19,
        leading=24,
        spaceAfter=8,
    ))

    story = []

    story.append(Paragraph(
        "RF Amplifier Verification Report",
        styles["ReportTitle"],
    ))

    story.append(Paragraph(
        "Automated RF Test and Verification System",
        styles["Normal"],
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Report generated:</b> " + timestamp,
        styles["Normal"],
    ))
    story.append(Paragraph(
        "<b>Measurement source:</b> Educational simulation; "
        "no physical RF instrument was connected.",
        styles["Normal"],
    ))
    story.append(Paragraph(
        "<b>Test mode:</b> "
        + ("Simulated fault injected" if inject_fault
           else "Normal simulated operation"),
        styles["Normal"],
    ))
    story.append(Spacer(1, 14))

    story.append(Paragraph("1. Test Configuration", styles["Heading2"]))

    configuration = [
        ["Parameter", "Value"],
        ["Start frequency", f"{START_FREQUENCY_GHZ:.2f} GHz"],
        ["Stop frequency", f"{STOP_FREQUENCY_GHZ:.2f} GHz"],
        ["Frequency points", str(NUMBER_OF_POINTS)],
        [
            "Minimum acceptable gain",
            f"{MINIMUM_ACCEPTABLE_GAIN_DB:.2f} dB",
        ],
        ["Injected fault drop", f"{FAULT_DROP_DB:.1f} dB"],
    ]

    config_table = Table(configuration, colWidths=[3.0 * inch, 3.3 * inch])
    config_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243B53")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(config_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("2. Verification Summary", styles["Heading2"]))

    summary_data = [
        ["Metric", "Result"],
        ["Total measurement points", str(summary["total_tests"])],
        ["Passed measurements", str(summary["passed"])],
        ["Failed measurements", str(summary["failed"])],
        [
            "Minimum measured gain",
            f'{summary["minimum_measured_gain_db"]:.3f} dB',
        ],
        [
            "Worst-case margin",
            f'{summary["worst_margin_db"]:+.3f} dB',
        ],
        ["Overall result", summary["overall_result"]],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[3.0 * inch, 3.3 * inch],
    )

    result_color = (
        colors.darkgreen
        if summary["overall_result"] == "PASS"
        else colors.darkred
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243B53")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("TEXTCOLOR", (1, -1), (1, -1), result_color),
        ("FONTNAME", (1, -1), (1, -1), "Helvetica-Bold"),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("3. Frequency Response", styles["Heading2"]))

    if Path(plot_file).exists():
        story.append(Image(
            str(plot_file),
            width=6.6 * inch,
            height=3.9 * inch,
        ))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The dashed line represents the configured minimum gain "
        "requirement. Measurements below this line fail the "
        "verification criterion.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 14))

    story.append(Paragraph(
        "4. Failed Measurement Points",
        styles["Heading2"],
    ))

    failed_results = [
        item for item in results if item["result"] == "FAIL"
    ]

    if failed_results:
        failed_data = [[
            "Frequency (GHz)",
            "Measured gain (dB)",
            "Margin (dB)",
        ]]

        for item in failed_results:
            failed_data.append([
                f'{item["frequency_ghz"]:.3f}',
                f'{item["measured_gain_db"]:.3f}',
                f'{item["margin_db"]:+.3f}',
            ])

        failed_table = Table(
            failed_data,
            repeatRows=1,
            colWidths=[2.2 * inch, 2.2 * inch, 1.9 * inch],
        )
        failed_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243B53")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        story.append(failed_table)
    else:
        story.append(Paragraph(
            "No measurements failed the configured requirement.",
            styles["Normal"],
        ))

    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "<b>Engineering note:</b> This report documents a software "
        "simulation. The amplifier response, injected fault, and "
        "acceptance threshold are illustrative and are not validated "
        "against actual satellite hardware specifications.",
        styles["Normal"],
    ))

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(
            letter[0] - 0.65 * inch,
            0.35 * inch,
            f"Page {document.page}",
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return pdf_file

# MAIN execution function for the RF test system

def main():
    print("=" * 60)
    print("AUTOMATED RF TEST AND VERIFICATION SYSTEM")
    print("EDUCATIONAL SIMULATION — NOT REAL RF MEASUREMENTS")
    print("=" * 60)

    choice = input("\nInject a simulated amplifier fault? (y/n): ")
    choice = choice.strip().lower()

    if choice not in {"y", "n"}:
        print("Invalid choice. Enter y or n.")
        return

    inject_fault = choice == "y"

    results = run_rf_test(inject_fault)
    summary = summarize_results(results)

    csv_file = export_results(results)
    plot_file = plot_results(results, inject_fault)

    pdf_file = generate_pdf_report(
        results,
        summary,
        plot_file,
        inject_fault=inject_fault,
    )

    print("\nTEST SUMMARY")
    print("-" * 40)
    print(f"Frequency points tested: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(
        f"Minimum measured gain: "
        f"{summary['minimum_measured_gain_db']:.3f} dB"
    )
    print(f"Worst-case margin: {summary['worst_margin_db']:+.3f} dB")
    print(f"Overall result: {summary['overall_result']}")

    print(f"\nCSV report: {csv_file}")
    print(f"Plot: {plot_file}")
    print(f"PDF engineering report: {pdf_file}")


if __name__ == "__main__":
    main()
