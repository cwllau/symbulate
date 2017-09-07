"""Data structures for storing the results of a simulation.

This module provides data structures for storing the
results of a simulation, either outcomes from a
probability space or realizations of a random variable /
random process.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from numbers import Number
from collections import Counter

from .sequences import TimeFunction
from .table import Table
from .utils import is_scalar, is_vector, get_dimension
from .plot import configure_axes, get_next_color, discrete_check
from statsmodels.graphics.mosaicplot import mosaic
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import NullFormatter
from matplotlib.transforms import Affine2D
from scipy.stats import gaussian_kde

plt.style.use('seaborn-colorblind')

def is_hashable(x):
    return x.__hash__ is not None

def count_var(x):
    counts = {}
    for val in x:
        if val in counts:
            counts[val] += 1
        else:
            counts[val] = 1
    return counts

class Results(list):

    def __init__(self, results):
        for result in results:
            self.append(result)

    def apply(self, fun):
        """Apply a function to each outcome of a simulation.

        Args:
          fun: A function to apply to each outcome.

        Returns:
          Results: A Results object of the same length,
            where each outcome is the result of applying
            the function to each outcome from the original
            Results object.
        """
        return type(self)(fun(x) for x in self)

    def __getitem__(self, i):
        return self.apply(lambda x: x[i])

    def get(self, i):
        for j, x in enumerate(self):
            if j == i:
                return x

    def _get_counts(self):
        counts = {}
        for x in self:
            if is_hashable(x):
                y = x
            elif isinstance(x, list) and all(is_hashable(i) for i in x):
                y = tuple(x)
            else:
                y = str(x)
            if y in counts:
                counts[y] += 1
            else:
                counts[y] = 1
        return counts

    def tabulate(self, outcomes=None, normalize=False):
        """Counts up how much of each outcome there were.

        Args:
          outcomes (list): A list of outcomes to tabulate.
            By default, will tabulate all outcomes that
            appear in the Results.  Use this option if
            you want to include outcomes that could
            potentially not appear in the Results.
          normalize (bool): If True, return the relative
            frequency. Otherwise, return the counts.
            Defaults to False.

        Returns:
          Table: A Table with each of the observed
            outcomes and their freuencies.
        """
        table = Table(self._get_counts(), outcomes)
        if normalize:
            return table / len(self)
        else:
            return table


    # The following functions return a Results object
    # with the outcomes that satisfy a given criterion.

    def filter(self, fun):
        """Filters the results of a simulation and
             returns only those outcomes that satisfy
             a given criterion.

        Args:
          fun (outcome -> bool): A function that
            takes in an outcome and returns a
            True / False. Only the outcomes that
            return True will be kept; the others
            will be filtered out.

        Returns:
          Results: Another Results object containing
            only those outcomes for which the function
            returned True.
        """
        return type(self)(x for x in self if fun(x))

    def filter_eq(self, value):
        return self.filter(lambda x: x == value)

    def filter_neq(self, value):
        return self.filter(lambda x: x != value)

    def filter_lt(self, value):
        return self.filter(lambda x: x < value)

    def filter_leq(self, value):
        return self.filter(lambda x: x <= value)

    def filter_gt(self, value):
        return self.filter(lambda x: x > value)

    def filter_geq(self, value):
        return self.filter(lambda x: x >= value)


    # The following functions return an integer indicating
    # how many outcomes passed a given criterion.

    def count(self, fun=lambda x: True):
        """Counts the number of outcomes that satisfied
             a given criterion.

        Args:
          fun (outcome -> bool): A function that
            takes in an outcome and returns a
            True / False. Only the outcomes that
            return True will be counted.

        Returns:
          int: The number of outcomes for which
            the function returned True.
        """
        return len(self.filter(fun))

    def count_eq(self, value):
        return len(self.filter_eq(value))

    def count_neq(self, value):
        return len(self.filter_neq(value))

    def count_lt(self, value):
        return len(self.filter_lt(value))

    def count_leq(self, value):
        return len(self.filter_leq(value))

    def count_gt(self, value):
        return len(self.filter_gt(value))

    def count_geq(self, value):
        return len(self.filter_geq(value))


    # The following functions define vectorized operations
    # on the Results object.

    def __eq__(self, other):
        return self.apply(lambda x: x == other)

    def __ne__(self, other):
        return self.apply(lambda x: x != other)

    def __lt__(self, other):
        return self.apply(lambda x: x < other)

    def __le__(self, other):
        return self.apply(lambda x: x <= other)

    def __gt__(self, other):
        return self.apply(lambda x: x > other)

    def __ge__(self, other):
        return self.apply(lambda x: x >= other)


    def plot(self):
        raise Exception("Only simulations of random variables (RV) "
                        "can be plotted, but you simulated from a " 
                        "probability space. You must first define a RV "
                        "on your probability space and simulate it. "
                        "Then call .plot() on those simulations.")
 
    def mean(self):
        raise Exception("You can only call .mean() on simulations of "
                        "random variables (RV), but you simulated from "
                        "a probability space. You must first define "
                        "a RV on your probability space and simulate it "
                        "Then call .mean() on those simulations.")

    def var(self):
        raise Exception("You can only call .var() on simulations of "
                        "random variables (RV), but you simulated from "
                        "a probability space. You must first define "
                        " a RV on your probability space and simulate it "
                        "Then call .var() on those simulations.")

    def sd(self):
        raise Exception("You can only call .sd() on simulations of "
                        "random variables (RV), but you simulated from "
                        "a probability space. You must first define "
                        " a RV on your probability space and simulate it "
                        "Then call .sd() on those simulations.")

    def corr(self):
        raise Exception("You can only call .corr() on simulations of "
                        "random variables (RV), but you simulated from "
                        "a probability space. You must first define "
                        " a RV on your probability space and simulate it "
                        "Then call .corr() on those simulations.")
   
    def cov(self):
        raise Exception("You can only call .cov() on simulations of "
                        "random variables (RV), but you simulated from "
                        "a probability space. You must first define "
                        " a RV on your probability space and simulate it "
                        "Then call .cov() on those simulations.")


    def _repr_html_(self):

        table_template = '''
    <table>
      <thead>
        <th width="10%">Index</th>
        <th width="90%">Result</th>
      </thead>
      <tbody>
        {table_body}
      </tbody>
    </table>
    '''
        row_template = '''
        <tr>
          <td>%s</td><td>%s</td>
        </tr>
        '''

        def truncate(result):
            if len(result) > 100:
                return result[:100] + "..."
            else:
                return result

        table_body = ""
        for i, x in enumerate(self):
            table_body += row_template % (i, truncate(str(x)))
            # if we've already printed 9 rows, skip to end
            if i >= 8:
                table_body += "<tr><td>...</td><td>...</td></tr>"
                i_last = len(self) - 1
                table_body += row_template % (i_last, truncate(str(self.get(i_last))))
                break
        return table_template.format(table_body=table_body)


class RVResults(Results):

    def plot(self, type=None, alpha=None, normalize=True, jitter=False, 
        bins=30, **kwargs):
        if type is not None:
            if isinstance(type, str):
                type = (type,)
            elif not isinstance(type, (tuple, list)):
                raise Exception("I don't know how to plot a " + str(type))
        
        dim = get_dimension(self)
        if dim == 1:
            counts = self._get_counts()
            heights = counts.values()
            discrete = discrete_check(heights)
            if type is None:
                if discrete:
                    type = ("impulse",)
                else:
                    type = ("hist",)
            if alpha is None:
                alpha = .5

            fig = plt.gcf()
            ax = plt.gca()
            color = get_next_color(ax)
            
            if 'density' in type:
                density = gaussian_kde(self)
                density.covariance_factor = lambda: 0.25
                density._compute_covariance()
                if discrete:
                    xs = sorted(list(counts.keys()))
                    ax.plot(xs, density(xs), marker='o', color=color, linestyle='-')
                else:
                    xs = np.linspace(min(self), max(self), 1000)
                    ax.plot(xs, density(xs), linewidth=2, color=color)

            if 'hist' in type or 'bar' in type:
                ax.hist(self, color=color, bins=bins, alpha=alpha, normed=True, **kwargs)
                plt.ylabel("Density" if normalize else "Count")
            elif 'impulse' in type:
                x = list(counts.keys())
                y = list(counts.values())
                if alpha is None:
                    alpha = .7
                if normalize:
                    y_tot = sum(y)
                    y = [i / y_tot for i in y]
                if jitter:
                    a = .02 * (max(x) - min(x))
                    noise = np.random.uniform(low=-a, high=a)
                    x = [i + noise for i in x]
                # plot the impulses
                ax.vlines(x, 0, y, color=color, alpha=alpha, **kwargs)
                configure_axes(ax, x, y, ylabel="Relative Frequency" if normalize else "Count")
            if 'rug' in type:
                if discrete:
                    self = self + np.random.normal(loc=0, scale=.002 * (max(self) - min(self)), size=len(self))
                ax.plot(list(self), [0.001]*len(self), '|', linewidth = 5, color='k')
                if len(type) == 1:
                    ax.yaxis.set_ticklabels([])
                    ax.yaxis.set_ticks([])
        elif dim == 2:
            x, y = zip(*self)

            x_count = count_var(x)
            y_count = count_var(y)
            x_height = x_count.values()
            y_height = y_count.values()
            
            discrete_x = discrete_check(x_height)
            discrete_y = discrete_check(y_height)

            if type is None:
                type = ("scatter",)

            if alpha is None:
                alpha = .5

            if 'marginal' in type:
                fig = plt.gcf()
                gs = GridSpec(4, 4)
                ax = fig.add_subplot(gs[1:4, 0:3])
                ax_marg_x = fig.add_subplot(gs[0, 0:3])
                ax_marg_y = fig.add_subplot(gs[1:4, 3])
                color = get_next_color(ax)
                if 'density' in type:
                    densityX = gaussian_kde(x)
                    densityX.covariance_factor = lambda: 0.25
                    densityX._compute_covariance()
                    densityY = gaussian_kde(y)
                    densityY.covariance_factor = lambda: 0.25
                    densityY._compute_covariance()
                    x_lines = np.linspace(min(x), max(x), 1000)
                    y_lines = np.linspace(min(y), max(y), 1000)
                    ax_marg_x.plot(x_lines, densityX(x_lines), linewidth=2, color=get_next_color(ax))
                    ax_marg_y.plot(y_lines, densityY(y_lines), linewidth=2, color=get_next_color(ax), 
                                  transform=Affine2D().rotate_deg(270) + ax_marg_y.transData)
                else:
                    if discrete_x:
                        x_key = list(x_count.keys())
                        x_val = list(x_height)
                        x_tot = sum(x_val)
                        x_val = [i / x_tot for i in x_val]
                        ax_marg_x.vlines(x_key, 0, x_val, color=get_next_color(ax), alpha=alpha, **kwargs)
                    else:
                        ax_marg_x.hist(x, color=get_next_color(ax), normed=True, 
                                       alpha=alpha, bins=bins)
                    if discrete_y:
                        y_key = list(y_count.keys())
                        y_val = list(y_height)
                        y_tot = sum(y_val)
                        y_val = [i / y_tot for i in y_val]
                        ax_marg_y.hlines(y_key, 0, y_val, color=get_next_color(ax), alpha=alpha, **kwargs)
                    else:
                        ax_marg_y.hist(y, color=get_next_color(ax), normed=True,
                                       alpha=alpha, bins=bins, orientation='horizontal')
                plt.setp(ax_marg_x.get_xticklabels(), visible=False)
                plt.setp(ax_marg_y.get_yticklabels(), visible=False)
            else:
                fig = plt.gcf()
                ax = plt.gca()
                color = get_next_color(ax)

            nullfmt = NullFormatter() #removes labels on fig

            if 'scatter' in type:
                if jitter:
                    x += np.random.normal(loc=0, scale=.01 * (max(x) - min(x)), size=len(x))
                    y += np.random.normal(loc=0, scale=.01 * (max(y) - min(y)), size=len(y))
                ax.scatter(x, y, alpha=alpha, c=color, **kwargs)
            elif 'hist' in type:
                histo = ax.hist2d(x, y, bins=bins, cmap='Blues')
                if 'marginal' not in type:
                    caxes = fig.add_axes([0, 0.1, 0.05, 0.8])
                else:
                    caxes = fig.add_axes([0, 0.1, 0.05, 0.57])
                cbar = plt.colorbar(mappable=histo[3], cax=caxes)
                caxes.yaxis.set_ticks_position('left')
                cbar.set_label('Density')
                caxes.yaxis.set_label_position("left")
            elif 'density' in type:
                res = np.vstack([x, y])
                density = gaussian_kde(res)
                xmax = max(x)
                xmin = min(x)
                ymax = max(y)
                ymin = min(y)
                Xgrid, Ygrid = np.meshgrid(np.linspace(xmin, xmax, 100),
                                           np.linspace(ymin, ymax, 100))
                Z = density.evaluate(np.vstack([Xgrid.ravel(), Ygrid.ravel()]))
                den = ax.imshow(Z.reshape(Xgrid.shape), origin='lower', cmap='Blues',
                          aspect='auto', extent=[xmin, xmax, ymin, ymax]
                )
                if 'marginal' not in type:
                    caxes = fig.add_axes([0, 0.1, 0.05, 0.8])
                else:
                    caxes = fig.add_axes([0, 0.1, 0.05, 0.57])
                cbar = plt.colorbar(mappable=den, cax=caxes)
                caxes.yaxis.set_ticks_position('left')
                cbar.set_label('Density')
                caxes.yaxis.set_label_position("left")
            elif 'tile' in type:
                res = np.array(self)

                idx = np.ravel_multi_index(res.T, res.max(0)+1)
                _, u_id, counts = np.unique(idx, return_index=True, return_counts=True)

                x_vals = res[u_id][:, 0]
                y_vals = res[u_id][:, 1]
                intensity = counts / len(x)

                x_uniq = np.unique(x_vals)
                y_uniq = np.unique(y_vals)
                intensity_frame = np.zeros(shape = (len(x_uniq) + 1, len(y_uniq) + 1))
                
                for i in range(len(x_vals)):
                    intensity_frame[x_vals[i] - 1][y_vals[i] - 1] = intensity[i - 1]

                x_axis = np.arange(intensity_frame.shape[0])
                y_axis = np.arange(intensity_frame.shape[1])
                hm = ax.pcolor(x_axis, y_axis, np.fliplr(np.rot90(intensity_frame, k=3)), cmap=plt.cm.Blues)

                if 'marginal' not in type:
                    caxes = fig.add_axes([0, 0.1, 0.05, 0.8])
                else:
                    caxes = fig.add_axes([0, 0.1, 0.05, 0.57])
                cbar = plt.colorbar(mappable=hm, cax=caxes)
                caxes.yaxis.set_ticks_position('left')
                cbar.set_label('Relative Frequency')
                caxes.yaxis.set_label_position("left")
            elif 'mixed-tile' in type:
                if not discrete_x:
                    bin_points = np.linspace(np.amin(x), np.amax(x), bins)
                    x = np.digitize(x, bin_points)
                if not discrete_y:
                    bin_points = np.linspace(np.amin(y), np.amax(y), bins)
                    y = np.digitize(y, bin_points)
                res = pd.DataFrame({'X': x, 'Y': y})
                res['num'] = 1
                res_pivot = pd.pivot_table(res, values='num', index=['Y'],
                    columns=['X'], aggfunc=np.sum)
                res_pivot = res_pivot / len(x)
                res_pivot[np.isnan(res_pivot)] = 0
                hm = ax.pcolor(res_pivot, cmap=plt.cm.Blues)
            elif 'violin' in type:
                res = np.array(self)
                values = []
                if discrete_x and not discrete_y:
                    positions = sorted(list(x_count.keys()))
                    for i in positions:
                        values.append(res[res[:, 0] == i, 1].tolist())
                    violins = ax.violinplot(dataset=values, showmedians=True)
                    ax.set_xticks(np.array(positions) + 1)
                    ax.set_xticklabels(positions)
                else: 
                    positions = sorted(list(y_count.keys()))
                    for i in positions:
                        values.append(res[res[:, 1] == i, 0].tolist())
                    violins = ax.violinplot(dataset=values, showmedians=True, vert=False)
                    ax.set_yticks(np.array(positions) + 1)
                    ax.set_yticklabels(positions)
                for part in violins['bodies']:
                    part.set_edgecolor('black')
                    part.set_alpha(alpha)
                for part in ('cbars', 'cmins', 'cmaxes', 'cmedians'):
                    vp = violins[part]
                    vp.set_edgecolor('black')
                    vp.set_linewidth(1)
        else:
            if alpha is None:
                alpha = .1
            for x in self:
                if not hasattr(x, "__iter__"):
                    x = [x]
                plt.plot(x, 'k.-', alpha=alpha, **kwargs)

    def cov(self, **kwargs):
        if get_dimension(self) == 2:
            return np.cov(self, rowvar=False)[0, 1]
        elif get_dimension(self) > 0:
            return np.cov(self, rowvar=False)
        else:
            raise Exception("Covariance requires that the simulation results have consistent dimension.")

    def corr(self, **kwargs):
        if get_dimension(self) == 2:
            return np.corrcoef(self, rowvar=False)[0, 1]
        elif get_dimension(self) > 0:
            return np.corrcoef(self, rowvar=False)
        else:
            raise Exception("Correlation requires that the simulation results have consistent dimension.")

    def mean(self):
        if all(is_scalar(x) for x in self):
            return np.array(self).mean()
        elif get_dimension(self) > 0:
            return tuple(np.array(self).mean(0))
        else:
            raise Exception("I don't know how to take the mean of these values.")

    def var(self):
        if all(is_scalar(x) for x in self):
            return np.array(self).var()
        elif get_dimension(self) > 0:
            return tuple(np.array(self).var(0))
        else:
            raise Exception("I don't know how to take the variance of these values.")

    def sd(self):
        if all(is_scalar(x) for x in self):
            return np.array(self).std()
        elif get_dimension(self) > 0:
            return tuple(np.array(self).std(0))
        else:
            raise Exception("I don't know how to take the variance of these values.")

    def standardize(self):
        mean_ = self.mean()
        sd_ = self.sd() 
        if all(is_scalar(x) for x in self):
            return RVResults((x - mean_) / sd_ for x in self)
        elif get_dimension(self) > 0:
            return RVResults((np.asarray(self) - mean_) / sd_)


class RandomProcessResults(Results):

    def __init__(self, results, timeIndex):
        self.timeIndex = timeIndex
        super().__init__(results)

    def __getitem__(self, t):
        return RVResults(x[t] for x in self)

    def plot(self, tmin=0, tmax=10, alpha=.1, **kwargs):
        if self.timeIndex.fs == float("inf"):
            ts = np.linspace(tmin, tmax, 200)
            style = "k-"
        else:
            nmin = int(np.floor(tmin * self.timeIndex.fs))
            nmax = int(np.ceil(tmax * self.timeIndex.fs))
            ts = [self.timeIndex[n] for n in range(nmin, nmax)]
            style = "k.--"
        for x in self:
            y = [x[t] for t in ts]
            plt.plot(ts, y, style, alpha=alpha, **kwargs)
        plt.xlabel("Time (t)")

        # expand the y-axis slightly
        axes = plt.gca()
        ymin, ymax = axes.get_ylim()
        buff = .05 * (ymax - ymin)
        plt.ylim(ymin - buff, ymax + buff)

    def mean(self):
        def fun(t):
            return self[t].mean()
        return TimeFunction(fun, self.timeIndex)

    def var(self):
        def fun(t):
            return self[t].var()
        return TimeFunction(fun, self.timeIndex)

    def sd(self):
        def fun(t):
            return self[t].sd()
        return TimeFunction(fun, self.timeIndex)

