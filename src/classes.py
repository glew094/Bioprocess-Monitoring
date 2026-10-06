
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
        mask = self.df.loc[:, "batch_id"] == batch_id
        return self.df.loc[mask, :].copy()



    def optimal_ph_mask(self, df_batch):
        """
        Determines whether each pH measurement falls within
        the acceptable operating range.
        """

        lower_bound = self.ph_lims[0]
        upper_bound = self.ph_lims[1]
        mask_1 = df_batch.loc[:, 'pH'] >= lower_bound
        mask_2  = df_batch.loc[:, 'pH'] <= upper_bound
        return mask_1 & mask_2

    def optimal_temperature_mask(self, df_batch):
        """
        Determines whether each temperature measurement falls
        within the acceptable operating range.
        """

        lower_bound = self.temperature_lims[0]
        upper_bound = self.temperature_lims[1]
        mask_T1 = df_batch.loc[:, 'temperature_C'] >= lower_bound
        mask_T2 = df_batch.loc[:, 'temperature_C'] <= upper_bound
        return mask_T1 & mask_T2


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

        #Glucose
        axes[0,0].scatter(
        df_batch.loc[:, "time_h"], df_batch.loc[:, "C_glucose_g_L^-1"],
        label = "Glucose", color = "tab:blue", marker = "o",
        s = 32, alpha = 0.7, edgecolor = "black", linewidth = 1
        )
        #Biomass
        axes[0,0].scatter(
        df_batch.loc[:, "time_h"], df_batch.loc[:, "C_biomass_g_L^-1"],
        label = "Biomass", color = "tab:orange", marker = "^",
        s = 32, alpha = 0.7, edgecolor = "black", linewidth = 1
        )
        #Product
        axes[0,0].scatter(
        df_batch.loc[:, "time_h"], df_batch.loc[:, "C_product_g_L^-1"],
        label = "Product", color = "tab:green", marker = "s",
        s = 32, alpha = 0.7, edgecolor = "black", linewidth = 1
        )
        axes[0,0].set_xlabel("Time [h]", fontsize = 10)
        axes[0,0].set_ylabel("Concentration [g/L]", fontsize = 10)
        axes[0,0].legend(fontsize = 10)

        # =======================================================================================
        #Top-Right Temperatures
        #========================================================================================

        mask_temp_optimal = self.optimal_temperature_mask(df_batch)
        mask_temp_suboptimal = ~mask_temp_optimal

        #Optimal values
        axes[0,1].scatter(
        df_batch.loc[mask_temp_optimal, "time_h"], df_batch.loc[mask_temp_optimal, "temperature_C"],
        label = "Optimal", color = "tab:green", marker = "o",
        s = 32, alpha = 0.7, edgecolor = "black", linewidth = 1
        )

        #Sub-Optimal values
        axes[0,1].scatter(
        df_batch.loc[mask_temp_suboptimal, "time_h"], df_batch.loc[mask_temp_suboptimal, "temperature_C"],
        label = "Sub-Optimal", color = "tab:red", marker = "X",
        s = 32, alpha = 0.7, edgecolor = "black", linewidth = 1
        )
        axes[0,1].set_xlabel("Time [h]", fontsize = 10)
        axes[0,1].set_ylabel("Temperature [°C]", fontsize = 10)
        axes[0,1].legend(fontsize = 10)

        # =======================================================================================
        #Bottom-Left pH
        #========================================================================================
        mask_ph_optimal = self.optimal_ph_mask(df_batch)
        mask_ph_suboptimal = ~mask_ph_optimal

        # Optimal values
        axes[1, 0].scatter(
            df_batch.loc[mask_ph_optimal, "time_h"], df_batch.loc[mask_ph_optimal, "pH"],
            label="Optimal", color="tab:green", marker="o",
            s=32, alpha=0.7, edgecolor="black", linewidth=1
        )

        # Sub-Optimal values
        axes[1, 0].scatter(
            df_batch.loc[mask_ph_suboptimal, "time_h"], df_batch.loc[mask_ph_suboptimal, "pH"],
            label="Sub-Optimal", color="tab:red", marker="X",
            s=32, alpha=0.7, edgecolor="black", linewidth=1
        )
        axes[1, 0].set_xlabel("Time [h]", fontsize=10)
        axes[1, 0].set_ylabel("pH", fontsize=10)
        axes[1, 0].legend(fontsize=10)

        # =======================================================================================
        # Bottom-Right Dissolved Oxygen
        # ========================================================================================
        axes[1, 1].scatter(
            df_batch.loc[:, "time_h"], df_batch.loc[:, "DO_percent"],
            label="DO %", color="tab:blue", marker="o",
            s=32, alpha=0.7, edgecolor="black", linewidth=1
        )
        axes[1, 1].set_xlabel("Time [h]", fontsize=10)
        axes[1, 1].set_ylabel("Dissolved Oxygen [%]", fontsize=10)
        axes[1, 1].legend(fontsize=10)

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
        """
        summary_data = []

        batch_ids = sorted(self.df.loc[:, "batch_id"].unique())

        for batch_id in batch_ids:
            df_batch = self.extract_batch(batch_id)

            #% of pH in optimal range
            mask_ph_optimal = self.optimal_ph_mask(df_batch)
            percent_ph_optimal = (mask_ph_optimal.sum() / len(mask_ph_optimal)) * 100

            #% of temperature in optimal range
            mask_temp_optimal = self.optimal_temperature_mask(df_batch)
            percent_temp_optimal = (mask_temp_optimal.sum() / len(mask_temp_optimal)) * 100

            idx_final = df_batch.loc[:, "time_h"].idxmax()

            c_product_final = df_batch.loc[idx_final, "C_product_g_L^-1"]

            summary_data.append({
                "batch_id": batch_id,
                "ph_optimal_percent": round(percent_ph_optimal, 2),
                "temperature_optimal_percent": round(percent_temp_optimal, 2),
                "C_product_g_L^-1": round(c_product_final, 2),
            })

        df_summary = pd.DataFrame(summary_data)
        df_summary.to_csv(filepath, index = False)
