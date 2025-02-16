# Child Growth Analyzer Development Documentation

## Version History
- v1.1.1: Added WHO growth standards with precise percentile calculations for both boys and girls
- v1.1.0: Added age calculator, improved UI, added taskbar icon
- v1.0.0: Initial release

## Key Components
1. **Main Application (main.py)**
   - Growth chart visualization
   - Multiple dataset management
   - Age calculator
   - Data import/export

2. **Build System**
   - PyInstaller for exe creation
   - Inno Setup for installer
   - Version info in file_version_info.txt

3. **Distribution**
   - create_distribution.py for packaging
   - setup.iss for installer configuration
   - SHA256 checksums for verification

## Future Improvements
Potential areas for enhancement:
- Add WHO growth standards
- Export to PDF
- Multiple language support
- Data backup functionality
- Cloud storage integration

## Build Instructions
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Create executable:
   ```bash
   pyinstaller child_growth_analyzer.spec
   ```

3. Create installer:
   - Open Inno Setup Compiler
   - Compile setup.iss

4. Create distribution package:
   ```bash
   python create_distribution.py
   ```

## Project Structure 