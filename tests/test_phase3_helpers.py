import numpy as np

from phase3_correlations import choose_method, outlier_share
from phase3_lisa import classify_lisa
from phase3_common import standardize


def test_standardize_has_zero_mean_and_unit_scale():
    z = standardize(np.array([1.0, 2.0, 3.0]))
    assert np.isclose(z.mean(), 0.0)
    assert np.isclose(z.std(ddof=0), 1.0)


def test_lisa_cluster_labels():
    assert classify_lisa(1, 0.01) == "High-High"
    assert classify_lisa(2, 0.01) == "Low-High"
    assert classify_lisa(3, 0.01) == "Low-Low"
    assert classify_lisa(4, 0.01) == "High-Low"
    assert classify_lisa(1, 0.25) == "Not significant"


def test_outlier_share_and_method_rule():
    x = np.arange(1.0, 101.0)
    y = 2.0 * x + 5.0
    method, diagnostics = choose_method(x, y)
    assert method == "pearson"
    assert diagnostics["x_outlier_share"] == 0.0

    skewed = np.array([1.0] * 95 + [100.0] * 5)
    method2, _ = choose_method(skewed, x)
    assert method2 == "spearman"
    assert outlier_share(skewed) > 0
