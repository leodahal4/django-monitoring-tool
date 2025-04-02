# Contributing

We welcome contributions to `django-health-metrics`! This guide outlines how to get started.

## Getting Started
1. **Fork the Repository**  
   Fork the project on GitHub: [https://github.com/leodahal4/django-health-metrics](https://github.com/leodahal4/django-health-metrics).

2. **Clone Your Fork**  
   ```bash
   git clone https://github.com/<your-username>/django-health-metrics.git
   cd django-health-metrics
   ```

3. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Example Project**  
   ```bash
   cd example
   python manage.py migrate
   python manage.py runserver
   ```

## Making Changes
1. **Create a Branch**  
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write Code**  
   - Add new features or fix bugs in `django_health_metrics/`.
   - Update tests in `django_health_metrics/tests/`.

3. **Run Tests**  
   ```bash
   pytest
   ```

4. **Commit Changes**  
   ```bash
   git add .
   git commit -m "Add your descriptive message here"
   ```

5. **Push to Your Fork**  
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit a Pull Request**  
   Open a pull request on GitHub against the `master` branch of the main repository.

## Guidelines
- Follow PEP 8 for Python code style.
- Write tests for new features or bug fixes.
- Update documentation in `docs/` if needed.
- Keep commits focused and descriptive.

## Development Tips
- Use the `example/` project to test changes locally.
- Ensure all optional dependencies (e.g., Redis) are mocked or available during testing.

## Questions?
Feel free to open an issue on GitHub or reach out to the maintainers.

Thank you for contributing!