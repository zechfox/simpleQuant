import { Injectable } from '@angular/core';
import { Strategy } from './strategy';
import { Parameter } from './parameter';
import { Headers, Http, Response } from '@angular/http';
import 'rxjs/add/operator/toPromise';

@Injectable()
  export class StrategyService {
    private strategiesUrl = '/strategies';  // URL to web api
    private strategyDetailUrl='/strategy/detail/'

    constructor(private http: Http) { }

    getStrategies(): Promise<Strategy[]> {
      return this.http.get(this.strategiesUrl)
                      .toPromise()
		      .then(this.extractData)
		      .catch(this.handleError);
    }
    getStrategyById(id: number): Promise<Strategy> {
      return this.getStrategies()
                 .then(strategies=> strategies.find(strategy => strategy.id === id));
    }

    getStrategyByName(name: string): Promise<Strategy> {
      return this.getStrategies()
                 .then(strategies=> strategies.find(strategy => strategy.name === name));
    }

    getStrategySourceCode(name: string): Promise<string> {
      let requestUrl = this.strategyDetailUrl + name + '/sourceCode';
      return this.http.get(requestUrl)
                      .toPromise()
		      .then(this.extractData)
		      .catch(this.handleError);

    }

    getStrategyCustomizeParameters(id: number): Promise<Parameter[]> {
      let requestUrl = this.strategyDetailUrl + id.toString() + '/customizParameters';
      return this.http.get(requestUrl)
                      .toPromise()
		      .then(this.extractData)
		      .catch(this.handleError);

    }
    private extractData(res: Response) {
      let body = res.json();
      return body as Strategy[] || { };
    }
    private handleError(error: any): Promise<any> {
      console.error('An error occurred', error); // for demo purposes only
      return Promise.reject(error.message || error);
    }
}

