import numpy as np

def calculate_fov(magnification:float):
    """
    Calculate FOVx and FOVy using power law decay.

    Args:
    - magnification (float): Magnification value.

    Returns:
    - fovx (float): Calculated FOVx.
    - fovy (float): Calculated FOVy.
    """
    # Hardcoded parameters obtained from curve fitting
    #see camerasepcs for better understanding 
    params_fovx = [362.92115517, -0.98089024]
    params_fovy = [274.66195716, -0.98534345]
    
    # Calculate FOVx and FOVy using power law decay
    fovx = power_law_decay(magnification, *params_fovx)
    fovy = power_law_decay(magnification, *params_fovy)
    
    return fovx, fovy

def power_law_decay(x, a, b):
    """
    Power law decay model function.

    Args:
    - x (float or array): Input value(s).
    - a (float): Coefficient.
    - b (float): Exponent.

    Returns:
    - y (float or array): Output value(s) calculated using the power law decay model.
    """
    return a * np.power(x, b)


# import numpy as np
# from scipy.optimize import curve_fit

# class CameraSpecs:
#     def __init__(self, magnification, field_of_view_x, field_of_view_y):
#         self.magnification = magnification
#         self.field_of_view_x = field_of_view_x
#         self.field_of_view_y = field_of_view_y
#         self.params_fovx = None
#         self.params_fovy = None

#     def fit_power_law_decay(self):
#         # Define the power-law decay model function
#         def power_law_decay(x, a, b):
#             return a * np.power(x, b)

#         # Perform curve fitting for FOVx
#         self.params_fovx, _ = curve_fit(power_law_decay, self.magnification, self.field_of_view_x)

#         # Perform curve fitting for FOVy
#         self.params_fovy, _ = curve_fit(power_law_decay, self.magnification, self.field_of_view_y)

#     def predict_fov(self, magnification_value):
#         if self.params_fovx is None or self.params_fovy is None:
#             raise ValueError("Fitting parameters not available. Call fit_power_law_decay first.")

#         fov_x_predicted = self.power_law_decay(magnification_value, *self.params_fovx)
#         fov_y_predicted = self.power_law_decay(magnification_value, *self.params_fovy)

#         return fov_x_predicted, fov_y_predicted

#     @staticmethod
#     def power_law_decay(x, a, b):
#         return a * np.power(x, b)

# # Initialize camera specifications object
# camera_specs = CameraSpecs(
#     [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220],
#     [37.8, 19.5, 13.0, 9.8, 7.8, 6.5, 5.6, 4.9, 4.3, 3.9, 3.6, 3.3, 3.0, 2.8, 2.6, 2.4, 2.3, 2.2, 2.1, 2.0, 1.9, 1.8],
#     [28.3, 14.6, 9.7, 7.3, 5.8, 4.8, 4.2, 3.6, 3.2, 2.9, 2.7, 2.4, 2.2, 2.1, 1.9, 1.8, 1.7, 1.6, 1.5, 1.5, 1.4, 1.3]
# )

# # Fit power law decay curve (only once)
# camera_specs.fit_power_law_decay()

# # Store the fitted parameters for later use
# params_fovx = camera_specs.params_fovx
# params_fovy = camera_specs.params_fovy

# # Predict FOV for a given magnification value
# magnification_value = 136.5
# fovx_predicted, fovy_predicted = CameraSpecs.power_law_decay(magnification_value, *params_fovx), CameraSpecs.power_law_decay(magnification_value, *params_fovy)
# print("Predicted FOVx:", fovx_predicted)
# print("Predicted FOVy:", fovy_predicted)
