import { Http, Response } from '@angular/http';
import { Headers, RequestOptions } from '@angular/http';
import { Injectable } from '@angular/core';
import { ObjectData } from './object-data';
import { Transition } from './transition';

@Injectable()
  export class TransitionService {
    private transitionsUrl = '/transitions';  // URL to web api
    private transitionDetailUrl='/transition/detail/';

    constructor(private http: Http) { }

    getTransitions(): Promise<Transition[]> {
      return this.http.get(this.transitionsUrl)
                      .toPromise()
		      .then(response => response.json() as Transition[])
		      .catch(this.handleError);
    }

    getTransition(id: number): Promise<Transition> {
      return this.getTransitions()
                 .then(transitions => transitions.find(transition => transition.id === id));
    }

    getTransitionObjectData(id: number): Promise<ObjectData> {
      let requestUrl = this.transitionDetailUrl + id.toString() + '/objectData';
      return this.http.get(requestUrl)
                      .toPromise()
		      .then(this.extractData)
		      .catch(this.handleError);
    }

    getTransitionResults(id: number): Promise<ObjectData> {
      let requestUrl = this.transitionDetailUrl + id.toString() + '/results';
      console.log(requestUrl);
      return this.http.get(requestUrl)
                      .toPromise()
		      .then(this.extractData)
		      .catch(this.handleError);
    }

    addNewTransition(payload: string): Promise<Transition> {
      let headers = new Headers({ 'Content-Type': 'application/json' });
      let options = new RequestOptions({ headers: headers });

      return this.http.post(this.transitionsUrl, { payload }, options)
                   .toPromise()
		   .then(this.extractData)
                   .catch(this.handleError);
    }

    updateTransition(payload: string, id:number): Promise<Transition> {
      let headers = new Headers({ 'Content-Type': 'application/json' });
      let options = new RequestOptions({ headers: headers });
      let requestUrl = this.transitionDetailUrl + id.toString()

      return this.http.post(requestUrl, { payload }, options)
                   .toPromise()
		   .then(this.extractData)
                   .catch(this.handleError);
    }

    private extractData(res: Response) {
      let body = res.json();
      return body || { };
    }

    private handleError (error: Response | any) {
      // In a real world app, we might use a remote logging infrastructure
      let errMsg: string;
      if (error instanceof Response) {
        const body = error.json() || '';
        const err = body.error || JSON.stringify(body);
        errMsg = `${error.status} - ${error.statusText || ''} ${err}`;
      } 
      else {
        errMsg = error.message ? error.message : error.toString();
      }
      console.error(errMsg);
      return Promise.reject(errMsg);
    }


}

