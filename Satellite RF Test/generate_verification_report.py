
import csv
from datetime import datetime
from pathlib import Path
import subprocess
import sys
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from verification import (
    C_N0_DB_HZ,
    MINIMUM_EB_N0_DB,
    TELEMETRY_SCENARIOS,
    verify_link,
)

# File paths for the report generation and traceability CSV.

PROJECT_FOLDER = Path(__file__).resolve().parent
TRACEABILITY_FILE = PROJECT_FOLDER / "requirements_traceability.csv"
OUTPUT_FOLDER = PROJECT_FOLDER / "results"
OUTPUT_FILE = OUTPUT_FOLDER / "voyager_verification_report.pdf"


# Style helper functions for the PDF report.

def make_table(data, widths, font_size=8):
    table = Table(data, colWidths=widths, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24476B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    return table


def para(value, style):
    #Wrap table text so long entries fit inside their cells.
    return Paragraph(str(value), style)
def run_automated_tests():
    #Run the project's complete pytest suite and capture its outcome.
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=PROJECT_FOLDER,
        capture_output=True,
        text=True,
    )

    output_lines = (
        result.stdout + "\n" + result.stderr
    ).splitlines()

    summary_lines = [
        line.strip()
        for line in output_lines
        if any(
            phrase in line.lower()
            for phrase in (
                " passed",
                " failed",
                " error",
                " skipped",
                " xfailed",
                " no tests ran",
            )
        )
    ]

    summary = (
        " | ".join(summary_lines[-3:])
        if summary_lines
        else "No standard pytest summary found. Check the test output."
    )

    return {
        "passed": result.returncode == 0,
        "exit_code": result.returncode,
        "summary": summary,
    }

# Generate the PDF report, including test results, verification outcomes, and traceability information.

def generate_report():
    test_run = run_automated_tests()
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    document = SimpleDocTemplate(
        str(OUTPUT_FILE),
        pagesize=landscape(letter),
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CustomReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=8,
    ))

    cell_style = ParagraphStyle(
        name="CellStyle",
        parent=styles["BodyText"],
        fontSize=7,
        leading=9,
        spaceAfter=0,
    )

    story = []

    # 1. Title Page

    story.append(para(
        "Voyager Spacecraft RF Link Verification Report",
        styles["CustomReportTitle"],
    ))

    story.append(Spacer(1, 12))

    story.append(para(
        "Automated Software Test Results",
        styles["Heading1"],
    ))

    test_status = (
        "PASS" if test_run["passed"] else "FAIL"
    )

    test_table = [
        ["Item", "Result"],
        ["Test command", "python -m pytest -q"],
        ["Overall test status", test_status],
        ["Pytest summary", para(test_run["summary"], cell_style)],
        ["Process exit code", str(test_run["exit_code"])],
    ]

    story.append(make_table(
        test_table,
        [2.0 * inch, 7.4 * inch],
    ))

    story.append(Spacer(1, 12))


    story.append(para(
        "Educational RF communications simulation",
        styles["Normal"],
    ))

    story.append(Spacer(1, 8))

    story.append(para(
        "<b>Generated:</b> "
        + datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        styles["Normal"],
    ))

    story.append(para(
        "<b>Measurement source:</b> Simulated calculations. "
        "No physical RF instruments or live spacecraft telemetry were connected.",
        styles["Normal"],
    ))

    story.append(Spacer(1, 12))

    # 2. Test Configuration

    story.append(para("1. Test Configuration", styles["Heading1"]))

    configuration = [
        ["Parameter", "Value"],
        ["Carrier-to-noise density ratio (C/N0)", f"{C_N0_DB_HZ:.2f} dB-Hz"],
        ["Minimum Eb/N0 criterion", f"{MINIMUM_EB_N0_DB:.2f} dB"],
        ["Criterion source", "Educational example; not an official NASA requirement"],
    ]

    story.append(make_table(
        configuration,
        [3.0 * inch, 6.0 * inch],
    ))

    story.append(Spacer(1, 12))

    # 3. Verification Results

    story.append(para("2. Verification Results", styles["Heading1"]))

    results = [[
        "Scenario",
        "Data Rate (bps)",
        "Eb/N0 (dB)",
        "Minimum (dB)",
        "Margin (dB)",
        "Result",
    ]]

    for scenario, rate in TELEMETRY_SCENARIOS.items():
        result = verify_link(
            C_N0_DB_HZ,
            rate,
            MINIMUM_EB_N0_DB,
        )

        results.append([
            scenario,
            f"{rate:,}",
            f"{result['eb_n0']:.2f}",
            f"{MINIMUM_EB_N0_DB:.2f}",
            f"{result['margin']:+.2f}",
            "PASS" if result["passed"] else "FAIL",
        ])

    story.append(make_table(
        results,
        [
            2.8 * inch,
            1.25 * inch,
            1.1 * inch,
            1.2 * inch,
            1.1 * inch,
            0.8 * inch,
        ],
    ))

    story.append(Spacer(1, 8))

    story.append(para(
        "Interpretation: a non-negative margin meets the configured "
        "educational criterion. These results do not establish actual "
        "Voyager operating capability.",
        styles["BodyText"],
    ))

    story.append(Spacer(1, 12))

    # 4. Requirements Traceability
    # Column names match the user's actual CSV.

    story.append(para(
        "3. Requirements Traceability",
        styles["Heading1"],
    ))

    if not TRACEABILITY_FILE.exists():
        raise FileNotFoundError(
            f"Traceability CSV not found: {TRACEABILITY_FILE}"
        )

    with open(
        TRACEABILITY_FILE,
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        required_columns = {
            "Requirement ID",
            "Requirement",
            "Verification Method",
            "Test File",
            "Test Function",
            "Expected Result",
            "Status",
        }

        if not reader.fieldnames or not required_columns.issubset(
            set(reader.fieldnames)
        ):
            raise ValueError(
                "CSV headers do not match the expected traceability format. "
                f"Found: {reader.fieldnames}"
            )

        traceability = [[
            "Requirement ID",
            "Requirement",
            "Method",
            "Test File / Function",
            "Expected Result",
            "Status",
        ]]

        for row in reader:
            traceability.append([
                para(row["Requirement ID"], cell_style),
                para(row["Requirement"], cell_style),
                para(row["Verification Method"], cell_style),
                para(
                    row["Test File"] + " / " + row["Test Function"],
                    cell_style,
                ),
                para(row["Expected Result"], cell_style),
                para(row["Status"], cell_style),
            ])

    story.append(make_table(
        traceability,
        [
            0.85 * inch,
            2.0 * inch,
            1.25 * inch,
            2.3 * inch,
            2.0 * inch,
            0.8 * inch,
        ],
        font_size=7,
    ))

    story.append(Spacer(1, 12))

    # 5. Limitations and Disclaimers

    story.append(para("4. Limitations", styles["Heading1"]))

    limitations = [
        "C/N0 is a fixed model input chosen by Melissa Choloniuk, not a live measurement.",
        "The minimum Eb/N0 criterion is illustrative, not a NASA requirement.",
        "Actual link performance depends on modulation, coding, receiver "
        "characteristics, system losses, and operating conditions.",
        "Traceability statuses are read from the CSV and are not independently "
        "confirmed by this report generator.",
    ]

    for item in limitations:
        story.append(para("- " + item, styles["BodyText"]))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 8))

    story.append(para(
        "End of report.",
        styles["Italic"],
    ))

    document.build(story)

    print("Verification report generated successfully.")
    print(f"Report location: {OUTPUT_FILE}")
    print(f"Traceability requirements included: {len(traceability) - 1}")


if __name__ == "__main__":
    generate_report()
