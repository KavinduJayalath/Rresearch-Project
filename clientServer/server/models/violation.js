const mongoose = require('mongoose');

const violationSchema = new mongoose.Schema(
  {
    type: {
      type: String,
      required: true,
      trim: true
    },
    year: {
      type: String,
      required: true,
      trim: true
    },
    month: {
      type: String,
      required: true,
      trim: true
    },
    day: {
      type: String,
      required: true,
      trim: true
    },
    time: {
      type: String,
      required: true,
      trim: true
    },
    location: {
      type: String,
      required: true,
      trim: true
    },
    camId: {
      type: String,
      required: true,
      trim: true
    },
    file_path: {
      type: String,
      required: true
    },
    file_mimetype: {
      type: String,
      required: true
    }
  },
  {
    timestamps: true
  }
);

const Violation = mongoose.model('violation', violationSchema);

module.exports = Violation;