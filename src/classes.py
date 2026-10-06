import os
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator

class BioprocessMonitor:
    def __init__(self, filepath, ph_lims, temperature_lims):
        """
        Utility class used to monitor bioprocesses by
        generating dashboards and summaries.
        """

        self.df = pd.read_csv(filepath)
        self.ph_lims = ph_lims
        self.temperature_lims = temperature_lims

    def extract_batch(self, batch_id):
        """
        Extracts data corresponding to a single batch.
        """
        return self.df.loc[:,batch_id] == batch_id



    def optimal_ph_mask(self, df_batch):
        """
        Determines whether each pH measurement falls within
        the acceptable operating range.
        """

        lower_bound = self.ph_lims[0]
        upper_bound = self.ph_lims[1]
        mask_pH = df_batch['pH'] >= lower_bound * df_batch['pH'] <= upper_bound
        return mask_pH

    def optimal_temperature_mask(self, df_batch):
        """
        Determines whether each temperature measurement falls
        within the acceptable operating range.
        """

        lower_bound = self.temperature_lims[0]
        upper_bound = self.temperature_lims[1]
        mask_T = df_batch['temperature'] >= lower_bound * df_batch['temperature'] <= upper_bound
        return mask_T


    def get_n_batches(self):
        """
        Determines the number of unique batches present
        in the dataset.
        """
        return  self.df['batch_id'].nunique()

    def export_dashboard(self, batch_id, filepath):
        """
        Creates and saves a dashboard figure for a single batch.

        """
        df_batch = self.extract_batch(batch_id)
        fig, axes = plt.subplots(2,2, figsize=(12,8), dpi = 200, layout = "constrained")

        # =======================================================================================
        #Top-Left Concentrations
        # =======================================================================================
        ax = [0,0]
        #Glucose
        ax.scatter(
        df_batch.loc[:, "time_h"], df_batch.loc[:, "C_glucose_g_L_^-1"],
        label = "Glucose", color = "tab:blue", marker = "o",
        s = 32, alpha = 0.7, edgecolor = "black", linewidth = 1
        )
        #Biomass
        ax.scatter(
        df_batch.loc[:, "time_h"], df_batch.loc[:, "C_biomass_g_L_^-1"],
        label = "Biomass", color = "tab:orange", marker = "^",
        s = 32, alpha = 0.7, edgecolor = "black", linewidth = 1
        )
        #Product
        ax.scatter(
        df_batch.loc[:, "time_h"], df_batch.loc[:, "C_product_g_L_^-1"],
        label = "Product", color = "tab:green", marker = "s",
        s = 32, alpha = 0.7, edgecolor = "black", linewidth = 1
        )
        ax.set_xlabel("Time [h]", fontsize = 10)
        ax.set_ylabel("Concentration [g/L]", fontsize = 10)
        ax.legend(fontsize = 10)

        # =======================================================================================
        #Top-Right Temperatures
        #========================================================================================
        ax = axes[0,1]
        mask_temp_optimal = self.optimal_temperature_mask(df_batch)
        mask_temp_suboptimal = ~mask_temp_optimal

        #Optimal values
        ax.scatter(
        df_batch.loc[mask_temp_optimal, "time_h"], df_batch.loc[mask_temp_optimal, "temperature_C"],
        label = "Optimal", color = "tab:green", marker = "o",
        s = 32, alpha = 0.7, edgecolor = "black", linewidth = 1
        )

        #Sub-Optimal values
        ax.scatter(
        df_batch.loc[mask_temp_suboptimal, "time_h"], df_batch.loc[mask_temp_suboptimal, "temperature_C"],
        label = "Sub-Optimal", color = "tab:red", marker = "X",
        s = 32, alpha = 0.7, edgecolor = "black", linewidth = 1
        )
        ax.set_xlabel("Time [h]", fontsize = 10)
        ax.set_ylabel("Temperature [°C]", fontsize = 10)
        ax.legend(fontsize = 10)

        # =======================================================================================
        #Bottom-Left pH
        #========================================================================================
        ax = axes[1, 0]
        mask_ph_optimal = self.optimal_ph_mask(df_batch)
        mask_ph_suboptimal = ~mask_ph_optimal

        # Optimal values
        ax.scatter(
            df_batch.loc[mask_ph_optimal, "time_h"], df_batch.loc[mask_ph_optimal, "temperature_C"],
            label="Optimal", color="tab:green", marker="o",
            s=32, alpha=0.7, edgecolor="black", linewidth=1
        )

        # Sub-Optimal values
        ax.scatter(
            df_batch.loc[mask_ph_suboptimal, "time_h"], df_batch.loc[mask_ph_suboptimal, "temperature_C"],
            label="Sub-Optimal", color="tab:red", marker="X",
            s=32, alpha=0.7, edgecolor="black", linewidth=1
        )
        ax.set_xlabel("Time [h]", fontsize=10)
        ax.set_ylabel("pH", fontsize=10)
        ax.legend(fontsize=10)

        # =======================================================================================
        # Bottom-Right Dissolved Oxygen
        # ========================================================================================
        ax = axes[1, 1]

        ax.scatter(
            df_batch.loc[:, "time_h"], df_batch.loc[:, "DO_percent"],
            label="DO %", color="tab:blue", marker="o",
            s=32, alpha=0.7, edgecolor="black", linewidth=1
        )
        ax.set_xlabel("Time [h]", fontsize=10)
        ax.set_ylabel("Dissolved Oxygen (%)", fontsize=10)
        ax.legend(fontsize=10)

        # =======================================================================================
        # Format
        # ========================================================================================

        for row in axes:
            for ax_curr in row:
                ax_curr.xaxis.set_major_locator(MultipleLocator(6))
                ax_curr.tick_params(axis='both', which = 'major', labelsize = 10)

        fig.savefig(filepath)
        plt.close(fig)

    def export_summary(self, filepath):
        """
        Generates a batch summary table and exports it to a CSV file.

        Parameters
        ----------
        filepath : str
            Output CSV table path.

        Summary Table Columns
        ---------------------
        batch_id
            Batch identifier.

        ph_optimal_percent
            Percentage of measurements in a batch within the
            acceptable pH range, rounded to 2 decimal places.

        temperature_optimal_percent
            Percentage of measurements in a batch within the
            acceptable temperature range, rounded to 2 decimal places.

        C_product_g_L^-1_final
            Final product concentration for the batch.
        """