import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, binary_sensor, select, text_sensor, canbus, text
from esphome.const import *
from esphome.components.canbus import CanbusComponent
#from esphome.const import (
#    ENTITY_CATEGORY_CONFIG,
#)

timer_ns = cg.esphome_ns.namespace("timer")
dakin_rotex_control_ns = cg.esphome_ns.namespace('dakin_rotex_control')
DakinHPC = dakin_rotex_control_ns.class_('DakinRotexControl', cg.Component)
TimerText = timer_ns.class_("TimerText", text.Text, cg.Component)
OperationModeSelect = dakin_rotex_control_ns.class_("OperationModeSelect", select.Select)

DEPENDENCIES = []

UNIT_BAR = "bar"
UNIT_LITER_PER_HOUR = "ltr/h"

AUTO_LOAD = ['sensor', 'select', 'text_sensor', 'binary_sensor']

CONF_CAN_ID = "canbus_id"
CONF_LOG_FILTER_TEXT = "log_filter_text"

CONF_TEMPERATURE_OUTSIDE = "temperature_outside"    # External temperature
CONF_TDHW1 = "tdhw1"
CONF_WATER_PRESSURE = "water_pressure"
CONF_WATER_FLOW = "water_flow"

CONF_OPERATION_MODE = "operation_mode"
CONF_ERROR_CODE = "error_code"

CONF_OPERATION_MODE_SELECT = "operation_mode_select"

ICON_SUN_SNOWFLAKE_VARIANT = "mdi:sun-snowflake-variant"

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(DakinHPC),
        cv.Required(CONF_CAN_ID): cv.use_id(CanbusComponent),
        cv.Optional(CONF_LOG_FILTER_TEXT): text.TEXT_SCHEMA.extend(
            {
                cv.GenerateID(): cv.declare_id(TimerText),
                cv.Optional(CONF_MODE, default="TEXT"): cv.enum(text.TEXT_MODES, upper=True),
            }
        ),

        ########## Sensors ##########

        cv.Optional(CONF_TEMPERATURE_OUTSIDE): sensor.sensor_schema(
            device_class=DEVICE_CLASS_TEMPERATURE,
            unit_of_measurement=UNIT_CELSIUS,
            accuracy_decimals=1,
            state_class=STATE_CLASS_MEASUREMENT
        ).extend(),
        cv.Optional(CONF_TDHW1): sensor.sensor_schema(
            device_class=DEVICE_CLASS_TEMPERATURE,
            unit_of_measurement=UNIT_CELSIUS,
            accuracy_decimals=1,
            state_class=STATE_CLASS_MEASUREMENT
        ).extend(),
        cv.Optional(CONF_WATER_PRESSURE): sensor.sensor_schema(
            device_class=DEVICE_CLASS_PRESSURE,
            unit_of_measurement=UNIT_BAR,
            accuracy_decimals=2,
            state_class=STATE_CLASS_MEASUREMENT
        ).extend(),
        cv.Optional(CONF_WATER_FLOW): sensor.sensor_schema(
            device_class=DEVICE_CLASS_WATER,
            unit_of_measurement=UNIT_LITER_PER_HOUR,
            accuracy_decimals=0,
            state_class=STATE_CLASS_MEASUREMENT
        ).extend(),

        ######## Text Sensors ########

        cv.Optional(CONF_OPERATION_MODE): text_sensor.text_sensor_schema(
            icon=ICON_SUN_SNOWFLAKE_VARIANT
        ).extend(),
        cv.Optional(CONF_ERROR_CODE): text_sensor.text_sensor_schema(
            icon="mdi:alert"
        ).extend(),

        ########## Selects ##########

        cv.Optional(CONF_OPERATION_MODE_SELECT): select.select_schema(
            OperationModeSelect,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon=ICON_SUN_SNOWFLAKE_VARIANT
        ).extend(),
    }
).extend(cv.COMPONENT_SCHEMA)

def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    yield cg.register_component(var, config)

    if CONF_CAN_ID in config:
        cg.add_define("USE_CANBUS")
        canbus = yield cg.get_variable(config[CONF_CAN_ID])
        cg.add(var.set_canbus(canbus))

    ########## Sensors ##########

    if temperature_outside := config.get(CONF_TEMPERATURE_OUTSIDE):
        sens = yield sensor.new_sensor(temperature_outside)
        cg.add(var.getAccessor().set_temperature_outside_sensor(sens))

    if tdhw1 := config.get(CONF_TDHW1):
        sens = yield sensor.new_sensor(tdhw1)
        cg.add(var.getAccessor().set_tdhw1(sens))

    if water_pressure := config.get(CONF_WATER_PRESSURE):
        sens = yield sensor.new_sensor(water_pressure)
        cg.add(var.getAccessor().set_water_pressure(sens))

    if water_flow := config.get(CONF_WATER_FLOW):
        sens = yield sensor.new_sensor(water_flow)
        cg.add(var.getAccessor().set_water_flow(sens))

    ######## Text Sensors ########

    if operation_mode := config.get(CONF_OPERATION_MODE):
        sens = yield text_sensor.new_text_sensor(operation_mode)
        cg.add(var.getAccessor().set_operation_mode_sensor(sens))

    if error_code := config.get(CONF_ERROR_CODE):
        sens = yield text_sensor.new_text_sensor(error_code)
        cg.add(var.getAccessor().set_error_code_sensor(sens))

    ########## Selects ##########

    operation_mode_options = ["Bereitschaft", "Heizen", "Absenken", "Sommer", "Kühlen", "Automatik 1", "Automatik 2"]

    if operation_mode_select := config.get(CONF_OPERATION_MODE_SELECT):
        s = yield select.new_select(operation_mode_select, options = operation_mode_options)
        yield cg.register_parented(s, var)
        cg.add(var.getAccessor().set_operation_mode_select(s))
