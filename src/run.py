from src import data
from src import plots
from src import model


def run():
    """
    Runs the full data gathering, processing and moddeling pipeline
    """

    # Get raw data
    raw_data = data.get_data()

    # Calculate new cases
    new_cases = data.new_cases(raw_data)

    # Get smoothed data
    original, smoothed = data.smooth_cases(new_cases)

    # Plot orginal vs smoothed
    plots.original_smoothed(original, smoothed)

    # Get posteriors from optimized Bayesian model
    posterior = model.bayesian_model(
        smoothed, p=0.95, save_posteriors_df=True, optimize=False
    )

    # Plot Rt estimate
    plots.plot_rt(posterior)


if __name__ == "__main__":
    run()
