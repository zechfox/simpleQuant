import { Parameter } from './parameter';

export class Transition {
  id: number;
  name: string;
  strategyName: string;
  object: string;
  duration: number;
  customizeParameter: string;

  constructor() {}

  updateFromJson(json: string): void {
    let updateJson = JSON.parse(json);
    this.updateFromObject(updateJson);
  }

  updateFromObject(object: Object): void {
    for (var proc in object) {
      this[proc] = object[proc];
    }
  }

  setParameters(parameters: string): void {
    this.customizeParameter = parameters;
  }
}

